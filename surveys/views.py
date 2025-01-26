from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Survey, Question, Choice, Response, Answer
from .forms import SurveyForm, QuestionForm, ChoiceForm
import logging

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        surveys = Survey.objects.all().filter(user=user).order_by('-created_at')
        return render(request, 'surveys/home.html', {
            'surveys': surveys,
            'user': user
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
                    
                    # Handle choices for multiple choice and checkbox
                    if q_type in ['multiple_choice', 'checkbox']:
                        # Construct the choices key dynamically
                        choices_key = f'choices_{index + 1}[]'
                        
                        # Get choices
                        choice_texts = request.POST.getlist(choices_key)
                        choice_texts = [choice.strip() for choice in choice_texts if choice.strip()]
                        
                        # Validate choices
                        if len(choice_texts) < 2:
                            raise ValidationError(f"Multiple Choice and Checkbox questions require at least two choices. Please add choices for the question: '{text}'.")
                        
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
            elif question.question_type in ['multiple_choice', 'checkbox']:
                # Handle multiple choice and checkbox answers
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
            
            elif question.question_type in ['multiple_choice', 'checkbox']:
                # Collect choice distribution
                choice_counts = {}
                for choice in question.choices.all():
                    choice_count = responses.filter(answers__question=question, answers__choice_answer=choice).count()
                    choice_counts[choice.text] = {
                        'count': choice_count,
                        'percentage': (choice_count / responses.count() * 100) if responses.count() > 0 else 0
                    }
                question_results['choices'] = choice_counts
            
            results[question.id] = question_results
        
        return render(request, 'surveys/survey_results.html', {
            'survey': survey,
            'results': results
        })
