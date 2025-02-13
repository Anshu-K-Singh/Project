from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RespondentProfileForm
from .models import Respondent
from surveys.models import SurveyNotification
from surveyapp.models import Poll, PollResponse, PollChoice

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
def respondent_dashboard(request):
    respondent = Respondent.objects.get(user=request.user)
    
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
    
    context = {
        'respondent': respondent,
        'unread_notifications': unread_notifications,
        'shared_polls': shared_polls,
        'voted_polls': voted_polls,
    }
    
    return render(request, 'respondent_app/respondent_dashboard.html', context)

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
