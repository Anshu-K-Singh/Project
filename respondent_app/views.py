from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RespondentProfileForm
from .models import Respondent, RespondentGroup
from surveys.models import SurveyNotification
from surveyapp.models import Poll, PollResponse, PollChoice, HostedSurvey

# Create your views here.
@login_required
def complete_respondent_profile(request):
    try:
        respondent = request.user.respondent
        if request.method == 'POST':
            form = RespondentProfileForm(request.POST, instance=respondent)
            if form.is_valid():
                form.save()
                return redirect('respondent_app:dashboard')  # Redirect to dashboard after profile completion
        else:
            form = RespondentProfileForm(instance=respondent)
        
        return render(request, 'respondent_app/complete_profile.html', {'form': form})
    except Respondent.DoesNotExist:
        # If no respondent profile exists, create one
        if request.method == 'POST':
            form = RespondentProfileForm(request.POST)
            if form.is_valid():
                respondent = form.save(commit=False)
                respondent.user = request.user
                respondent.save()
                return redirect('respondent_app:dashboard')
        else:
            form = RespondentProfileForm()
        
        return render(request, 'respondent_app/complete_profile.html', {'form': form})



@login_required
def edit_profile(request):
    user = request.user
    try:
        respondent = user.respondent
        if request.method == 'POST':
            form = RespondentProfileForm(request.POST, instance=respondent)
            if form.is_valid():
                form.save()
                return redirect('respondent_app:dashboard')  # Redirect to dashboard after saving
        else:
            form = RespondentProfileForm(instance=respondent)
        return render(request, 'respondent_app/edit_profile.html', {'form': form})
    except Respondent.DoesNotExist:
        return redirect('respondent_app:complete_profile')

from django.db.models import Q
@login_required
def respondent_dashboard(request):
    respondent = Respondent.objects.get(user=request.user)
    # Get hosted surveys for the respondent's groups
    hosted_surveys = HostedSurvey.objects.filter(
        Q(assigned_groups__in=respondent.groups.all()) | Q(assigned_groups__isnull=True),
        is_active=True
    ).distinct()
    
    # Check if profile is complete
    profile_complete = all([
        respondent.mobile, 
        respondent.dob, 
        respondent.gender, 
        respondent.zipcode, 
        respondent.education, 
        respondent.employment, 
        respondent.race
    ])
    
    if not profile_complete:
        return redirect('respondent_app:complete_profile')
    
    # Get unread survey notifications
    unread_notifications = SurveyNotification.objects.filter(
        user=request.user, 
        is_read=False
    ).select_related('survey')

    survey_notification_count = unread_notifications.count()
    
    # Get shared polls that the respondent hasn't voted on
    shared_polls = Poll.objects.filter(
        respondents=request.user
    ).exclude(
        responses__respondent=request.user
    ).order_by('-created_at')
    
    # Get polls the respondent has already voted on
    voted_polls = Poll.objects.filter(
        responses__respondent=request.user
    )
    completed_surveys = Response.objects.filter(user=request.user)
    total_points = sum(response.survey.points for response in completed_surveys)
    
    context = {
        'respondent': respondent,
        'unread_notifications': unread_notifications,
        'survey_notification_count': survey_notification_count,
        'shared_polls': shared_polls,
        'voted_polls': voted_polls,
        'total_points': total_points,
        'hosted_surveys': hosted_surveys
    }
    
    return render(request, 'respondent_app/respondent_dashboard.html', context)


from surveys.models import Response, Survey
@login_required
def survey_history(request):
    try:
        # Ensure the user has a complete profile
        respondent = request.user.respondent
        profile_complete = all([
            respondent.mobile, 
            respondent.dob, 
            respondent.gender, 
            respondent.zipcode, 
            respondent.education, 
            respondent.employment, 
            respondent.race
        ])
        
        if not profile_complete:
            return redirect('respondent_app:complete_profile')
        
        # Fetch user's survey responses with related survey details
        responses = Response.objects.filter(
            user=request.user
        ).select_related(
            'survey'
        ).order_by('-submitted_at')
        
        context = {
            'responses': responses
        }
        
        return render(request, 'respondent_app/survey_history.html', context)
    except Respondent.DoesNotExist:
        return redirect('respondent_app:complete_profile')


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
@login_required
@require_POST
@csrf_protect
def delete_survey_history(request, response_id):
    try:
        # Fetch the specific survey response
        survey_response = Response.objects.get(
            id=response_id, 
            user=request.user
        )
        
        # Delete the survey response
        survey_response.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Survey history deleted successfully.'
        })
    except Response.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Survey history not found or you do not have permission to delete it.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        }, status=500)


from surveys.models import Survey
from django.utils.timezone import now, timedelta
@login_required
def survey_wall(request):
    surveys = Survey.objects.all()
    taken_surveys = Response.objects.filter(user=request.user)
    # Get IDs of surveys taken more than 48 hours ago (should be hidden)
    expired_taken_ids = taken_surveys.filter(
        submitted_at__lt=now() - timedelta(hours=48)
    ).values_list('survey_id', flat=True)
    # Get IDs of all surveys taken by the user
    all_taken_ids = taken_surveys.values_list('survey_id', flat=True)
    # Identify new surveys (never taken by the user)
    new_survey_ids = surveys.exclude(id__in=all_taken_ids).values_list('id', flat=True)
    # Surveys should remain visible if they are:
    # 1. Never taken
    # 2. Taken within the last 48 hours
    valid_surveys = surveys.exclude(id__in=expired_taken_ids)
    context = {
        'surveys': valid_surveys,
        'new_survey_ids': list(new_survey_ids),
    }
    return render(request, 'respondent_app/surveywall.html', context)

    































@login_required
def take_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Check if poll is shared with the respondent
    if request.user not in poll.respondents.all():
        messages.error(request, 'You are not authorized to take this poll.')
        return redirect('respondent_app:dashboard')
    
    # Check if respondent has already voted
    if PollResponse.objects.filter(poll=poll, respondent=request.user).exists():
        messages.warning(request, 'You have already voted on this poll.')
        return redirect('respondent_app:dashboard')
    
    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if choice_id:
            choice = get_object_or_404(PollChoice, id=choice_id, poll=poll)
            
            PollResponse.objects.create(
                poll=poll,
                respondent=request.user,
                choice=choice
            )
            
            # Increment vote count
            choice.votes += 1
            choice.save()
            
            messages.success(request, 'Your vote has been recorded!')
            return redirect('respondent_app:dashboard')
    
    context = {
        'poll': poll
    }
    return render(request, 'respondent_app/take_poll.html', context)
