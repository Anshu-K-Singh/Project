from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account_app.forms import UserRegisterForm
from django.http import JsonResponse
from .models import SignUpTrend, UserDemographic, UserInsight, UserSource
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AffiliateForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Surveymonitor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import Survey
from .models import Survey, Question,Response # Assuming models are created for storing survey, questions, and options
import csv
import json
from django.views.decorators.csrf import csrf_exempt
import random






# Home view protected by login_required
@login_required
def home(request):

    # You can pass context to the template
    context = {
        'title': 'Home Page',  # Title to be shown in the template
        'message': 'Welcome to the Home Page!',
    }

    # Render the template and get the response
    response = render(request, 'surveyapp/home.html', context)

    # Add cache control headers to prevent caching of the page
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response



# Dashboard view (no login required here)
def dashboard(request):
    # Render dashboard page (no cache control required here as it doesn't require authentication)
    return render(request, 'surveyapp/dashboard.html')




# Another view (mdashboard) (no login required)
def mdashboard(request):
    # Render home page again but no cache control as it is public
    return render(request, 'surveyapp/home.html')




# View to fetch the table data
def fetch_table_data(request):
    """Fetch table data for SignUpTrend, UserDemographic, UserInsight, and UserSource models."""
    sign_up_trends = SignUpTrend.objects.all().values('date', 'total_signups')
    user_demographics = UserDemographic.objects.all().values('user_id', 'age_group', 'gender', 'location')
    user_insights = UserInsight.objects.all().values('user_id', 'satisfaction_score', 'feedback')
    user_sources = UserSource.objects.all().values('user_id', 'source')

    # Prepare data for the frontend
    data = {
        'sign_up_trends': list(sign_up_trends),
        'user_demographics': list(user_demographics),
        'user_insights': list(user_insights),
        'user_sources': list(user_sources)
    }

    # Return data as a JSON response
    return JsonResponse(data)





def affiliate_view(request):
    if request.method == 'POST':
        form = AffiliateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Affiliate information has been successfully added.')
            return redirect('affiliate')  # Redirect to the same page
    else:
        form = AffiliateForm()

    return render(request, 'surveyapp/affiliate.html', {'form': form})





#VIEWS FOR SURVEY MONITOR
def survey_monitor(request):
    # Fetch all surveys
    surveys = Surveymonitor.objects.all()
    return render(request, 'surveyapp/monitorsurvey.html', {'surveys': surveys})





def add_survey(request):
    if request.method == "POST":
        survey_name = request.POST.get('survey_name')
        survey_description = request.POST.get('survey_description')

        # Create the survey
        survey = Survey.objects.create(name=survey_name, description=survey_description)

        # Process the questions (assuming you're getting JSON questions data)
        question_data = request.POST.getlist('questions')
        for question_json in question_data:
            question = json.loads(question_json)
            choices = question.get('choices', [])
            mc_options = question.get('mcOptions', [])

            # Create the question
            Question.objects.create(
                survey=survey,
                text=question['question'],
                answer_type=question['answer_type'],
                required=question.get('required', False),
                choices=','.join(choices) if question['answer_type'] in ['multipleChoice', 'dropdown'] else '',
            )

        # After creating the survey, redirect to the survey form with the newly created survey_id
        return redirect('responseform', survey_id=survey.id)

    return render(request, 'surveyapp/addsurvey.html')


#VIEWS FOR SURVEY FORM
def response_form(request, survey_id=None):
    if survey_id:
        try:
            # Fetch the survey by its ID
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            # Handle if the survey is not found
            return redirect('responseform')  # Redirect or show an error page
        
        # Debug: print the survey name and questions
        print("Survey Name:", survey.name)
        print("Survey Description:", survey.description)
        print("Questions:", survey.questions.all())

        # Preprocess questions and choices (split choices by comma if applicable)
        questions = survey.questions.all()
        for question in questions:
            if question.choices:  # Assuming choices are stored as a comma-separated string
                question.choices_list = question.choices.split(',')  # Split into a list
            else:
                question.choices_list = []  # Empty list for questions without choices

        # Handle form submission
        if request.method == 'POST':
            answers = request.POST.getlist('answers[]')
            print("Form Answers:", answers)
            # Optionally save the answers or process them

        # Return the page with survey and questions
        return render(request, 'surveyapp/responseform.html', {'survey': survey, 'questions': questions})

    else:
        # If no survey_id is provided, render a fallback page
        return render(request, 'surveyapp/responseform.html')



# View to delete a question
def delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return JsonResponse({"status": "success", "message": "Question deleted successfully"})
    except Question.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Question not found"})


# View to edit a question
def edit_question(request, question_id):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        answer_type = request.POST.get('answer_type')

        try:
            question = Question.objects.get(id=question_id)
            question.question_text = question_text
            question.answer_type = answer_type
            question.save()

            return JsonResponse({"status": "success", "message": "Question updated successfully"})
        except Question.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Question not found"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})   



#VIEWS FOR SURVEY DETAILS
def survey_details(request):
    survey_data = {
        "duration": 10,
        "quota": 10,
        "status": "Active",
        "priority": "High",
        "description": "----description----",
        "urls": {
            "survey_url": "url.com",
            "social_survey_url": "socialmedia.url.com",
            "report_url": "report.url.com"
        },
        "values": {
            "complete_points": 100,
            "over_quota_points": 0,
            "terminate_points": 0
        }
    }
    return render(request, 'surveyapp/surveydetails.html', {"survey": survey_data, "survey_id": 1})  # Replace '1' with actual survey ID from database

@csrf_exempt
def deactivate_survey(request):
    if request.method == "POST":
        # Add logic to deactivate the survey (e.g., update database or change state)
        return JsonResponse({"status": "Survey deactivated"})
    return JsonResponse({"error": "Invalid request method"}, status=400)



def submit_survey(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        responses = data.get('responses')

        # Process the responses here (e.g., save to the database)

        return JsonResponse({"status": "success", "message": "Survey submitted successfully!"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})