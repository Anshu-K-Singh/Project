from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Survey, Question, Choice, Response, Answer
from .forms import SurveyForm, QuestionForm, ChoiceForm
from django.db.models import Count
import logging
import csv
from django.http import HttpResponse
from django.utils.text import slugify

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
        
        # Get question and choice data directly from POST
        question_texts = request.POST.getlist('question_text')
        question_types = request.POST.getlist('question_type')
        
        if not question_texts:
            messages.error(request, "At least one question is required.")
            return render(request, 'surveys/create_survey.html', {
                'survey_form': survey_form
            })
        
        try:
            with transaction.atomic():
                # Save survey
                survey = survey_form.save(commit=False)
                survey.user = request.user
                survey.save()
                
                # Process and save questions
                for index, (text, q_type) in enumerate(zip(question_texts, question_types)):
                    # Create question
                    question = Question.objects.create(
                        text=text,
                        question_type=q_type,
                        survey=survey
                    )
                    
                    # Handle choices for multiple choice, checkbox, and radio
                    if q_type in ['multiple_choice', 'checkbox', 'radio']:
                        # Construct the choices key dynamically
                        choices_key = f'choices_{index + 1}[]'
                        
                        # Get choices
                        choice_texts = request.POST.getlist(choices_key)
                        choice_texts = [choice.strip() for choice in choice_texts if choice.strip()]
                        
                        # Validate choices
                        if len(choice_texts) < 2:
                            raise ValidationError(f"Multiple Choice, Checkbox, and Radio questions require at least two choices. Please add choices for the question: '{text}'.")
                        
                        # Create choices
                        for choice_text in choice_texts:
                            Choice.objects.create(
                                question=question,
                                text=choice_text
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
        return render(request, 'surveys/survey_detail.html', {'survey': survey})

class TakeSurveyView(View):
    def get(self, request, unique_link):
        survey = get_object_or_404(Survey, unique_link=unique_link)
        return render(request, 'surveys/take_survey.html', {'survey': survey})
    
    def post(self, request, unique_link):
        survey = get_object_or_404(Survey, unique_link=unique_link)
        
        # Validate all questions are answered
        for question in survey.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            if not answer:
                messages.error(request, f"Question '{question.text}' must be answered.")
                return render(request, 'surveys/take_survey.html', {'survey': survey})
        
        # Create a new response
        response = Response.objects.create(survey=survey)
        
        # Process answers for each question
        for question in survey.questions.all():
            if question.question_type == 'text':
                text_answer = request.POST.get(f'question_{question.id}')
                if text_answer:
                    Answer.objects.create(
                        response=response,
                        question=question,
                        text_answer=text_answer
                    )
            elif question.question_type in ['multiple_choice', 'checkbox', 'radio']:
                # Handle multiple choice, checkbox, and radio answers
                choice_ids = request.POST.getlist(f'question_{question.id}')
                for choice_id in choice_ids:
                    choice = Choice.objects.get(id=choice_id)
                    Answer.objects.create(
                        response=response,
                        question=question,
                        choice_answer=choice
                    )
        
        messages.success(request, "Survey submitted successfully!")
        return render(request, 'surveys/survey_completed.html')

class SurveyResultsView(LoginRequiredMixin, View):
    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
        responses = survey.responses.all()
        
        # Prepare results data
        results = {}
        for question in survey.questions.all():
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
            
            results[question.id] = question_results
        
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
        headers.extend([question.text for question in survey.questions.all()])
        writer.writerow(headers)
        
        # Write response data
        for response_obj in survey.responses.all():
            row = [response_obj.id]
            
            # Get answers for each question
            for question in survey.questions.all():
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
        
        # Prepare to track existing and new questions
        existing_question_ids = list(survey.questions.values_list('id', flat=True))
        
        # Create new questions
        question_texts = request.POST.getlist('question_text')
        question_types = request.POST.getlist('question_type')
        
        for i, question_text in enumerate(question_texts):
            # Check if this is an existing question or a new one
            if i < len(existing_question_ids):
                # Update existing question
                question = Question.objects.get(id=existing_question_ids[i])
                question.text = question_text
                question.question_type = question_types[i]
                question.save()
            else:
                # Create new question
                question = Question.objects.create(
                    survey=survey,
                    text=question_text,
                    question_type=question_types[i]
                )
            
            # Handle choices for multiple choice, checkbox, and radio questions
            if question_types[i] in ['multiple_choice', 'checkbox', 'radio']:
                # Get existing choices for this question
                existing_choices = list(question.choices.all())
                
                # Get new choices from form
                choices_key = f'choices_{i}[]'
                new_choice_texts = request.POST.getlist(choices_key)
                
                # Update or create choices
                for j, choice_text in enumerate(new_choice_texts):
                    if j < len(existing_choices):
                        # Update existing choice
                        existing_choice = existing_choices[j]
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
        
        # Remove any extra existing questions
        if len(question_texts) < len(existing_question_ids):
            for extra_question_id in existing_question_ids[len(question_texts):]:
                Question.objects.get(id=extra_question_id).delete()
        
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
            num_questions=Count('questions')
        )
        
        context = {
            'surveys': surveys,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'name_filter': name_filter,
            'status_filter': status_filter,
        }
        
        return render(request, 'surveys/survey_history.html', context)