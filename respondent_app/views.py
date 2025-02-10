from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RespondentProfileForm
from .models import Respondent
from surveys.models import SurveyNotification

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
    try:
        respondent = request.user.respondent
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
        
        context = {
            'unread_notifications': unread_notifications,
        }
        
        return render(request, 'respondent_app/respondent_dashboard.html', context)
    except Respondent.DoesNotExist:
        return redirect('respondent_app:complete_profile')
