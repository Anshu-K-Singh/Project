from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Survey, Question, Choice, Response, Answer, SurveyDistribution, SurveyNotification, SurveyPage
from .forms import SurveyForm, QuestionForm, ChoiceForm
from django.db.models import Count, F
import logging
import csv
from django.http import HttpResponse
from django.utils.text import slugify
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import send_mail
from django.conf import settings
from respondent_app.models import RespondentGroup
from django.utils import timezone


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        # Filter only active surveys for the current user
        surveys = Survey.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        return render(request, 'surveys/home.html', {
            'surveys': surveys,
            'user': request.user
        })

class CreateSurveyView(LoginRequiredMixin, View):
    def get(self, request):
        survey_form = SurveyForm()
        return render(request, 'surveys/create_survey.html', {
            'survey_form': survey_form
        })
    
    def post(self, request):
        survey_form = SurveyForm(request.POST)
        
        if not survey_form.is_valid():
            return render(request, 'surveys/create_survey.html', {
                'survey_form': survey_form
            })
        
        try:
            with transaction.atomic():
                # Save survey
                survey = survey_form.save(commit=False)
                survey.user = request.user
                survey.save()
                
                # Process pages and questions
                page_titles = request.POST.getlist('page_title[]')
                page_orders = request.POST.getlist('page_order[]')
                question_texts = request.POST.getlist('question_text')
                question_types = request.POST.getlist('question_type')
                
                if not page_titles:
                    messages.error(request, "At least one page is required.")
                    return render(request, 'surveys/create_survey.html', {
                        'survey_form': survey_form
                    })
                
                # Create pages
                for i, (title, order) in enumerate(zip(page_titles, page_orders)):
                    page = SurveyPage.objects.create(
                        survey=survey,
                        title=title,
                        order=int(order)
                    )
                    
                    # Get questions for this page
                    page_questions = request.POST.getlist(f'page_{i}_question_text')
                    page_question_types = request.POST.getlist(f'page_{i}_question_type')
                    
                    if not page_questions:
                        messages.error(request, f"At least one question is required for page: {title}")
                        raise ValidationError(f"Page {title} requires at least one question.")
                    
                    # Process questions for this page
                    for j, (text, q_type) in enumerate(zip(page_questions, page_question_types)):
                        question = Question.objects.create(
                            survey=survey,
                            page=page,
                            text=text,
                            question_type=q_type
                        )
                        
                        # Handle choices for multiple choice questions
                        if q_type in ['multiple_choice', 'checkbox', 'radio']:
                            choices_key = f'page_{i}_question_{j}_choices[]'
                            eligibility_flag_key = f'page_{i}_question_{j}_is_eligibility_flag[]'
                            
                            choice_texts = request.POST.getlist(choices_key)
                            eligibility_flags = request.POST.getlist(eligibility_flag_key)
                            
                            choice_texts = [choice.strip() for choice in choice_texts if choice.strip()]
                            
                            if len(choice_texts) < 2:
                                raise ValidationError(f"Multiple Choice, Checkbox, and Radio questions require at least two choices. Please add choices for the question: '{text}'")
                            
                            for k, choice_text in enumerate(choice_texts):
                                Choice.objects.create(
                                    question=question,
                                    text=choice_text,
                                    is_eligibility_flag=k < len(eligibility_flags) and eligibility_flags[k] == 'on'
                                )
                
                messages.success(request, "Survey created successfully!")
                return redirect('surveys:survey_detail', survey_id=survey.id)
                
        except Exception as e:
            messages.error(request, f"Error creating survey: {str(e)}")
            return render(request, 'surveys/create_survey.html', {
                'survey_form': survey_form
            })

class SurveyDetailView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        
        # Get user's respondent groups
        respondent_groups = RespondentGroup.objects.filter(created_by=request.user)
        
        # Get survey distribution history
        distribution_history = SurveyDistribution.objects.filter(survey=survey).order_by('-created_at')
        
        return render(request, 'surveys/survey_detail.html', {
            'survey': survey,
            'respondent_groups': respondent_groups,
            'distribution_history': distribution_history
        })

class TakeSurveyView(View):
    def get(self, request, unique_link):
        # Try to find survey by unique_link (for authenticated users)
        survey = Survey.objects.filter(unique_link=unique_link).first()
        if not survey:
            # Try to find survey by external_link (for anonymous users)
            survey = get_object_or_404(Survey, external_link=unique_link)
        
        # Check survey expiry
        if survey.expiry_datetime and timezone.now() > survey.expiry_datetime:
            survey.is_expired = True
            survey.save(update_fields=['is_expired'])
            return render(request, 'surveys/survey_closed.html', {'survey': survey})

        # Check if external response limit is reached
        if survey.max_external_responses and survey.external_response_count >= survey.max_external_responses:
            return render(request, 'surveys/survey_closed.html', {'survey': survey})

        # For authenticated users, check if they've already responded
        if request.user.is_authenticated:
            existing_response = Response.objects.filter(survey=survey, user=request.user).exists()
            if existing_response:
                messages.warning(request, "You have already responded to this survey.")
                return redirect('respondent_app:dashboard')
        
        # Get current page from session or default to first page
        current_page = request.session.get(f'survey_{survey.id}_current_page', 0)
        total_pages = survey.pages.count()
        
        # If current_page is beyond total pages, reset to first page
        if current_page >= total_pages:
            current_page = 0
            request.session[f'survey_{survey.id}_current_page'] = current_page
        
        # Get the current page object
        current_page_obj = survey.pages.all()[current_page]
        
        return render(request, 'surveys/take_survey.html', {
            'survey': survey,
            'current_page': current_page,
            'total_pages': total_pages,
            'current_page_obj': current_page_obj,
            'progress': int((current_page / total_pages) * 100) if total_pages > 0 else 0
        })

    def post(self, request, unique_link):
        # Try to find survey by unique_link (for authenticated users)
        survey = Survey.objects.filter(unique_link=unique_link).first()
        if not survey:
            # Try to find survey by external_link (for anonymous users)
            survey = get_object_or_404(Survey, external_link=unique_link)
        
        # Check survey expiry
        if survey.expiry_datetime and timezone.now() > survey.expiry_datetime:
            survey.is_expired = True
            survey.save(update_fields=['is_expired'])
            return render(request, 'surveys/survey_closed.html', {'survey': survey})

        # Check if external response limit is reached
        if survey.max_external_responses and survey.external_response_count >= survey.max_external_responses:
            return render(request, 'surveys/survey_closed.html', {'survey': survey})

        # For authenticated users, check if they've already responded
        if request.user.is_authenticated:
            existing_response = Response.objects.filter(survey=survey, user=request.user).exists()
            if existing_response:
                messages.warning(request, "You have already responded to this survey.")
                return redirect('respondent_app:dashboard')

        # Get current page information
        current_page = request.session.get(f'survey_{survey.id}_current_page', 0)
        total_pages = survey.pages.count()
        current_page_obj = survey.pages.all()[current_page]
        
        # Check if it's a navigation request
        if 'prev_page' in request.POST:
            if current_page > 0:
                current_page -= 1
                request.session[f'survey_{survey.id}_current_page'] = current_page
            return redirect('surveys:take_survey', unique_link=unique_link)
            
        # Store answers in session for the current page
        page_answers = {}
        for question in current_page_obj.questions.all():
            if question.question_type == 'text':
                answer = request.POST.get(f'question_{question.id}')
                if answer:
                    page_answers[str(question.id)] = {'type': 'text', 'answer': answer}
            else:
                answers = request.POST.getlist(f'question_{question.id}')
                if answers:
                    page_answers[str(question.id)] = {'type': question.question_type, 'answers': answers}
        
        # Store answers in session
        survey_answers = request.session.get(f'survey_{survey.id}_answers', {})
        survey_answers[str(current_page)] = page_answers
        request.session[f'survey_{survey.id}_answers'] = survey_answers

        # Validate current page
        for question in current_page_obj.questions.all():
            # Check if question has eligibility flags
            if question.choices.filter(is_eligibility_flag=True).exists():
                user_answers = request.POST.getlist(f'question_{question.id}')
                if not user_answers:
                    messages.error(request, f"Question '{question.text}' must be answered.")
                    return render(request, 'surveys/take_survey.html', {
                        'survey': survey,
                        'current_page': current_page,
                        'total_pages': total_pages,
                        'current_page_obj': current_page_obj,
                        'progress': int((current_page / total_pages) * 100) if total_pages > 0 else 0
                    })
                
                # Check if any selected choice is an eligibility choice
                is_question_eligible = any(
                    Choice.objects.filter(id=choice_id, is_eligibility_flag=True).exists()
                    for choice_id in user_answers
                )
                if not is_question_eligible:
                    # Redirect to ineligibility page instead of showing an error message
                    return redirect('surveys:survey_ineligible', unique_link=unique_link, question_text=question.text)
                if not is_question_eligible:
                    messages.error(request, f"You are not eligible to take this survey. Only specific option(s) for '{question.text}' are allowed.")
                    return render(request, 'surveys/take_survey.html', {
                        'survey': survey,
                        'current_page': current_page,
                        'total_pages': total_pages,
                        'current_page_obj': current_page_obj,
                        'progress': int((current_page / total_pages) * 100) if total_pages > 0 else 0
                    })

        # If this is not the last page, move to next page
        if 'next_page' in request.POST and current_page < total_pages - 1:
            current_page += 1
            request.session[f'survey_{survey.id}_current_page'] = current_page
            return redirect('surveys:take_survey', unique_link=unique_link)
        
        # If this is the final submission
        if 'submit_survey' in request.POST:
            # Create response and store all answers
            with transaction.atomic():
                response = Response.objects.create(
                    survey=survey,
                    user=request.user if request.user.is_authenticated else None
                )
                
                # Process all stored answers
                survey_answers = request.session.get(f'survey_{survey.id}_answers', {})
                for page_answers in survey_answers.values():
                    for question_id, answer_data in page_answers.items():
                        question = Question.objects.get(id=question_id)
                        
                        if answer_data['type'] == 'text':
                            Answer.objects.create(
                                response=response,
                                question=question,
                                text_answer=answer_data['answer']
                            )
                        else:
                            for choice_id in answer_data['answers']:
                                choice = Choice.objects.get(id=choice_id)
                                Answer.objects.create(
                                    response=response,
                                    question=question,
                                    choice_answer=choice
                                )
                
                # Increment external response count if it's an external response
                if not request.user.is_authenticated:
                    survey.external_response_count = F('external_response_count') + 1
                    survey.save()
                
                # Clear session data
                request.session.pop(f'survey_{survey.id}_current_page', None)
                request.session.pop(f'survey_{survey.id}_answers', None)
                
                messages.success(request, "Survey submitted successfully!")
                return render(request, 'surveys/survey_completed.html')

class SurveyResultsView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        responses = survey.responses.all()
        
        # Prepare results data
        results = {}
        for page in survey.pages.all():
            page_results = {
                'title': page.title,
                'questions': []
            }
            
            for question in page.questions.all():
                question_results = {
                    'text': question.text,
                    'type': question.question_type,
                    'responses': []
                }
                
                if question.question_type == 'text':
                    # Collect text responses
                    text_responses = []
                    for response in responses:
                        try:
                            answer = response.answers.get(question=question)
                            if answer.text_answer:
                                text_responses.append(answer.text_answer)
                        except Answer.DoesNotExist:
                            pass
                    question_results['responses'] = text_responses
                
                elif question.question_type in ['multiple_choice', 'checkbox', 'radio']:
                    # Collect choice distribution
                    choice_counts = {}
                    total_responses = responses.filter(answers__question=question).count()
                    
                    for choice in question.choices.all():
                        choice_count = responses.filter(answers__question=question, answers__choice_answer=choice).count()
                        choice_counts[choice.text] = {
                            'count': choice_count,
                            'percentage': (choice_count / total_responses * 100) if total_responses > 0 else 0
                        }
                    question_results['choices'] = choice_counts
                
                page_results['questions'].append(question_results)
            
            results[page.id] = page_results
        
        return render(request, 'surveys/survey_results.html', {
            'survey': survey,
            'results': results
        })

class ExportSurveyCSVView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        # Get the survey
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        
        # Create HttpResponse with CSV mime type
        response = HttpResponse(content_type='text/csv')
        
        # Create a filename using survey title (slugified)
        filename = f"{slugify(survey.title)}_responses.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Prepare headers: Response ID + Questions
        headers = ['Response ID']
        for page in survey.pages.all():
            for question in page.questions.all():
                headers.append(question.text)
        writer.writerow(headers)
        
        # Write response data
        for response_obj in survey.responses.all():
            row = [response_obj.id]
            
            # Get answers for each question
            for page in survey.pages.all():
                for question in page.questions.all():
                    try:
                        answer = response_obj.answers.get(question=question)
                        
                        # Handle different question types
                        if question.question_type == 'text':
                            row.append(answer.text_answer or '')
                        elif question.question_type in ['multiple_choice', 'checkbox', 'radio']:
                            # For choice-based questions, get choice text
                            row.append(answer.choice_answer.text if answer.choice_answer else '')
                        else:
                            row.append('')
                    except Answer.DoesNotExist:
                        row.append('')
            
            writer.writerow(row)
        
        return response

class DeactivateSurveyView(LoginRequiredMixin, View):
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        survey.is_active = False
        survey.save()
        messages.success(request, f"Survey '{survey.title}' has been deactivated.")
        return redirect('surveys:home')

class EditSurveyView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        return render(request, 'surveys/edit_survey.html', {'survey': survey})
    
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        
        # Update survey details
        survey.title = request.POST.get('title')
        survey.description = request.POST.get('description')
        survey.save()
        
        # Prepare to track existing and new pages
        existing_page_ids = list(survey.pages.values_list('id', flat=True))
        
        # Create new pages
        page_titles = request.POST.getlist('page_title')
        page_orders = request.POST.getlist('page_order')
        
        for i, (title, order) in enumerate(zip(page_titles, page_orders)):
            # Check if this is an existing page or a new one
            if i < len(existing_page_ids):
                # Update existing page
                page = SurveyPage.objects.get(id=existing_page_ids[i])
                page.title = title
                page.order = int(order)
                page.save()
            else:
                # Create new page
                page = SurveyPage.objects.create(
                    survey=survey,
                    title=title,
                    order=int(order)
                )
            
            # Prepare to track existing and new questions
            existing_question_ids = list(page.questions.values_list('id', flat=True))
            
            # Create new questions
            question_texts = request.POST.getlist(f'page_{i}_question_text')
            question_types = request.POST.getlist(f'page_{i}_question_type')
            
            for j, (text, q_type) in enumerate(zip(question_texts, question_types)):
                # Check if this is an existing question or a new one
                if j < len(existing_question_ids):
                    # Update existing question
                    question = Question.objects.get(id=existing_question_ids[j])
                    question.text = text
                    question.question_type = q_type
                    question.save()
                else:
                    # Create new question
                    question = Question.objects.create(
                        survey=survey,
                        page=page,
                        text=text,
                        question_type=q_type
                    )
                
                # Handle choices for multiple choice, checkbox, and radio questions
                if q_type in ['multiple_choice', 'checkbox', 'radio']:
                    # Get existing choices for this question
                    existing_choices = list(question.choices.all())
                    
                    # Get new choices from form
                    choices_key = f'page_{i}_question_{j}_choices[]'
                    new_choice_texts = request.POST.getlist(choices_key)
                    
                    # Update or create choices
                    for k, choice_text in enumerate(new_choice_texts):
                        if k < len(existing_choices):
                            # Update existing choice
                            existing_choice = existing_choices[k]
                            existing_choice.text = choice_text
                            existing_choice.save()
                        else:
                            # Create new choice
                            Choice.objects.create(
                                question=question,
                                text=choice_text
                            )
                    
                    # Remove any extra existing choices
                    if len(new_choice_texts) < len(existing_choices):
                        for extra_choice in existing_choices[len(new_choice_texts):]:
                            extra_choice.delete()
        
        # Remove any extra existing pages
        if len(page_titles) < len(existing_page_ids):
            for extra_page_id in existing_page_ids[len(page_titles):]:
                SurveyPage.objects.get(id=extra_page_id).delete()
        
        messages.success(request, "Survey updated successfully!")
        return redirect('surveys:survey_detail', survey_id=survey.id)

class SurveyHistoryView(LoginRequiredMixin, View):
    def get(self, request):
        # Get sorting parameter
        sort_by = request.GET.get('sort', 'created_at')
        sort_order = request.GET.get('order', 'desc')
        
        # Get filter parameters
        name_filter = request.GET.get('name', '')
        status_filter = request.GET.get('status', '')
        
        # Base queryset (include both active and inactive surveys)
        surveys = Survey.objects.filter(user=request.user)
        
        # Apply name filter
        if name_filter:
            surveys = surveys.filter(title__icontains=name_filter)
        
        # Apply status filter
        if status_filter:
            surveys = surveys.filter(is_active=(status_filter == 'active'))
        
        # Apply sorting
        if sort_order == 'asc':
            surveys = surveys.order_by(sort_by)
        else:
            surveys = surveys.order_by(f'-{sort_by}')
        
        # Annotate with number of responses and questions
        surveys = surveys.annotate(
            num_responses=Count('responses'),
        )
        
        context = {
            'surveys': surveys,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'name_filter': name_filter,
            'status_filter': status_filter,
        }
        
        return render(request, 'surveys/survey_history.html', context)

class ExportSurveyPDFView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        # Get the survey
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        
        # Create a response with PDF mime type
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="survey_{survey.title}_details.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles['Title'].clone('CustomTitle')
        title_style.fontSize = 16
        title_style.spaceAfter = 12

        heading_style = styles['Heading2'].clone('CustomHeading')
        heading_style.fontSize = 12
        heading_style.spaceAfter = 6

        normal_style = styles['Normal'].clone('CustomNormal')
        normal_style.fontSize = 10
        normal_style.spaceAfter = 6

        # Collect story (content) for PDF
        story = []
        
        # Survey Title
        story.append(Paragraph("Survey Details", title_style))
        story.append(Spacer(1, 6))
        
        # Survey Metadata
        story.append(Paragraph(f"<b>Title:</b> {survey.title}", normal_style))
        story.append(Paragraph(f"<b>Description:</b> {survey.description or 'No description provided'}", normal_style))
        story.append(Paragraph(f"<b>Created On:</b> {survey.created_at.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Paragraph(f"<b>Total Questions:</b> {survey.questions.count()}", normal_style))
        story.append(Spacer(1, 12))
        
        # Pages Section
        story.append(Paragraph("Survey Pages", heading_style))
        story.append(Spacer(1, 6))
        
        for page in survey.pages.all():
            # Page Header
            story.append(Paragraph(f"Page {page.order}: {page.title}", normal_style))
            story.append(Spacer(1, 6))
            
            # Questions for this page
            for question in page.questions.all():
                # Question Header
                story.append(Paragraph(f"Question: {question.text}", normal_style))
                story.append(Paragraph(f"<b>Type:</b> {question.get_question_type_display()}", normal_style))
                
                # Choices for multiple choice questions
                if question.question_type in ['multiple_choice', 'checkbox', 'radio']:
                    choices = question.choices.all()
                    if choices:
                        choice_text = ", ".join([choice.text for choice in choices])
                        story.append(Paragraph(f"<b>Choices:</b> {choice_text}", normal_style))
                
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        return response

class UpdateExternalResponsesView(LoginRequiredMixin, View):
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        try:
            max_responses = int(request.POST.get('max_external_responses', 0))
            if max_responses < 0:
                raise ValueError("Maximum responses cannot be negative")
            
            # If new limit is less than current count, show error
            if max_responses > 0 and max_responses < survey.external_response_count:
                messages.error(request, 
                    f"Cannot set maximum responses to {max_responses} as there are already {survey.external_response_count} responses collected.")
                return redirect('surveys:survey_detail', survey_id=survey.id)
            
            survey.max_external_responses = max_responses if max_responses > 0 else None
            survey.save()
            messages.success(request, "Maximum external responses updated successfully!")
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('surveys:survey_detail', survey_id=survey.id)

class SendSurveyToGroupView(LoginRequiredMixin, View):
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        group_id = request.POST.get('respondent_group')
        points = request.POST.get('points')
        if not group_id:
            messages.error(request, "Please select a respondent group.")
            return redirect('surveys:survey_detail', survey_id=survey_id)

        try:
            group = RespondentGroup.objects.get(id=group_id, created_by=request.user)
            group_users = group.respondents.all()

            if not group_users:
                messages.warning(request, "The selected group has no respondents.")
                return redirect('surveys:survey_detail', survey_id=survey_id)

            sent_count = 0
            notification_count = 0

            for respondent in group_users:
                existing_response = Response.objects.filter(survey=survey, user=respondent.user).exists()

                if not existing_response:
                    notification, created = SurveyNotification.objects.get_or_create(
                        user=respondent.user,
                        survey=survey,
                        defaults={'is_read': False}
                    )

                    if created:
                        notification_count += 1
                        sent_count += 1
                        messages.success(request, f"Survey notification sent to {respondent.user.username} in group {group.name}")

                        # Debugging output
                        print(f"Preparing email for {respondent.user.username}")

                        subject = f"New Survey Available: {survey.title}"
                        message = (
                            f"Hello {respondent.user.username},\n\n"
                            f"You have been invited to take part in a new survey: \"{survey.title}\".\n"
                            f"Click the link below to participate:\n"
                            f"Thank you!"
                        )
                        recipient_email = respondent.user.email

                        if recipient_email:
                           
                            try:
                                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
                               
                            except Exception as e:
                                print(f"Email error: {str(e)}")
                        else:
                            print(f"Skipping email: No email found for {respondent.user.username}")

            if sent_count > 0:
                messages.success(request, f"Survey notifications sent to {notification_count} respondents in the {group.name} group.")
            else:
                messages.info(request, "No new respondents were found for this survey in the selected group.")

            survey.points = points
            survey.save()
            return redirect('surveys:survey_detail', survey_id=survey.id)

        except RespondentGroup.DoesNotExist:
            messages.error(request, "Selected respondent group not found.")
            return redirect('surveys:survey_detail', survey_id=survey_id)
        except Exception as e:
            print(f"View error: {str(e)}")  # Debugging
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('surveys:survey_detail', survey_id=survey_id)

class UpdateSurveyExpiryView(LoginRequiredMixin, View):
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        
        try:
            # Get expiry datetime from form
            expiry_str = request.POST.get('expiry_datetime')
            
            if expiry_str:
                # Parse the datetime 
                expiry_datetime = timezone.datetime.fromisoformat(expiry_str)
                
                # Ensure the datetime is timezone-aware
                if timezone.is_naive(expiry_datetime):
                    expiry_datetime = timezone.make_aware(expiry_datetime)
                
                # Update survey expiry
                survey.expiry_datetime = expiry_datetime
                survey.check_expiry()  # This will set is_expired if needed
                survey.save()
                
                messages.success(request, f"Survey expiry set to {expiry_datetime}")
            else:
                # If no datetime provided, clear the expiry
                survey.expiry_datetime = None
                survey.is_expired = False
                survey.save()
                
                messages.success(request, "Survey expiry cleared")
            
            return redirect('surveys:survey_detail', survey_id=survey.id)
        
        except ValueError:
            messages.error(request, "Invalid datetime format")
            return redirect('surveys:survey_detail', survey_id=survey.id)


class SurveyIneligibilityView(View):
    def get(self, request, unique_link, question_text):
        """
        Display an ineligibility page when a user does not select the required eligibility flag.
        
        Args:
            request: HTTP request object
            unique_link: Survey's unique link
            question_text: Text of the question with eligibility flags
        """
        return render(request, 'surveys/403.html', {
            'unique_link': unique_link,
            'question_text': question_text
        })