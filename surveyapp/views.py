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
from .models import Surveymonitor
from surveys.models import Survey, Response, Question   
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_authenticated and user.is_superuser



# Home view protected by login_required

@user_passes_test(is_superuser, login_url='/account/login/')
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
    user = request.user
    surveys = Survey.objects.all().filter(user=user)
    total_surveys = surveys.count()
    total_responses = Response.objects.all().count()
    context = {
        'user': user,
        'surveys': surveys,
        'total_surveys': total_surveys,
        'total_responses': total_responses
    }
    return render(request, 'surveyapp/dashboard.html', context)

# Another view (mdashboard) (no login required)
def mdashboard(request):
    return render(request, 'surveyapp/mdashboard.html')

# View to fetch the table data
def fetch_table_data(request):
    # Fetch table data for SignUpTrend, UserDemographic, UserInsight, and UserSource models.
    signuptrend_data = list(SignUpTrend.objects.values())
    userdemographic_data = list(UserDemographic.objects.values())
    userinsight_data = list(UserInsight.objects.values())
    usersource_data = list(UserSource.objects.values())

    data = {
        'signuptrend_data': signuptrend_data,
        'userdemographic_data': userdemographic_data,
        'userinsight_data': userinsight_data,
        'usersource_data': usersource_data
    }
    return JsonResponse(data)





def affiliate_view(request):
    if request.method == 'POST':
        form = AffiliateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('affiliate')
    else:
        form = AffiliateForm()
    return render(request, 'surveyapp/affiliate.html', {'form': form})


    #VIEWS FOR SURVEY MONITOR
def monitorsurvey(request):
    # Get sorting parameter
    sort_by = request.GET.get('sort', 'created_at')
    sort_order = request.GET.get('order', 'desc')
    
    # Get filter parameters
    name_filter = request.GET.get('name', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
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
    
    # Annotate with number of responses
    surveys = surveys.annotate(num_responses=Count('responses'))
    
    context = {
        'surveys': surveys,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'name_filter': name_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'surveyapp/monitorsurvey.html', context)

@login_required
def profiling(request):
    # Fetch all respondents and filter based on profile completeness
    from respondent_app.models import Respondent
    
    # Get all respondents and filter based on profile completeness
    all_respondents = Respondent.objects.all()
    completed_respondents = []
    
    for respondent in all_respondents:
        profile_complete = all([
            respondent.mobile, 
            respondent.dob, 
            respondent.gender, 
            respondent.zipcode, 
            respondent.education, 
            respondent.employment, 
            respondent.race
        ])
        
        if profile_complete:
            completed_respondents.append(respondent)
    
    # Apply filters from GET parameters
    gender = request.GET.get('gender')
    education = request.GET.get('education')
    employment = request.GET.get('employment')
    race = request.GET.get('race')
    country = request.GET.get('country')
    job_function = request.GET.get('job_function')
    job_industry = request.GET.get('job_industry')
    job_level = request.GET.get('job_level')
    company_size = request.GET.get('company_size')
    
    # Apply filters
    if gender:
        completed_respondents = [r for r in completed_respondents if r.gender == gender]
    if education:
        completed_respondents = [r for r in completed_respondents if r.education == education]
    if employment:
        completed_respondents = [r for r in completed_respondents if r.employment == employment]
    if race:
        completed_respondents = [r for r in completed_respondents if r.race == race]
    if country:
        completed_respondents = [r for r in completed_respondents if r.country == country]
    if job_function:
        completed_respondents = [r for r in completed_respondents if r.job_function == job_function]
    if job_industry:
        completed_respondents = [r for r in completed_respondents if r.job_industry == job_industry]
    if job_level:
        completed_respondents = [r for r in completed_respondents if r.job_level == job_level]
    if company_size:
        completed_respondents = [r for r in completed_respondents if r.company_size == company_size]
    
    # Prepare filter choices
    filter_choices = {
        'genders': Respondent.GENDER_CHOICES,
        'educations': Respondent.EDUCATION_CHOICES,
        'employments': Respondent.EMPLOYMENT_CHOICES,
        'races': Respondent.RACE_CHOICES,
        'countries': Respondent.COUNTRY_CHOICES,
        'job_functions': Respondent.JOB_FUNCTION_CHOICES,
        'job_industries': Respondent.JOB_INDUSTRY_CHOICES,
        'job_levels': Respondent.JOB_LEVEL_CHOICES,
        'company_sizes': Respondent.COMPANY_SIZE_CHOICES,
    }
    
    context = {
        'completed_respondents': completed_respondents,
        'title': 'Profiling',
        'filter_choices': filter_choices,
        'current_filters': {
            'gender': gender,
            'education': education,
            'employment': employment,
            'race': race,
            'country': country,
            'job_function': job_function,
            'job_industry': job_industry,
            'job_level': job_level,
            'company_size': company_size,
        }
    }
    
    return render(request, 'surveyapp/profiling.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token
from respondent_app.models import Respondent

@login_required
def get_respondent_details(request, respondent_id):
    respondent = get_object_or_404(Respondent, id=respondent_id)
    
    # Prepare respondent details
    details = {
        'username': respondent.user.username,
        'email': respondent.user.email,
        'first_name': respondent.user.first_name,
        'last_name': respondent.user.last_name,
        'mobile': respondent.mobile or 'N/A',
        'dob': respondent.dob.strftime('%d %B %Y') if respondent.dob else 'N/A',
        'gender': respondent.gender or 'N/A',
        'zipcode': respondent.zipcode or 'N/A',
        'education': respondent.education or 'N/A',
        'employment': respondent.employment or 'N/A',
        'race': respondent.race or 'N/A',
        'is_superuser': request.user.is_superuser
    }
    
    return JsonResponse(details)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def delete_respondent(request, respondent_id):
    respondent = get_object_or_404(Respondent, id=respondent_id)
    
    # Delete the associated user and respondent
    user = respondent.user
    respondent.delete()
    user.delete()
    
    return JsonResponse({'status': 'success'})

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from respondent_app.models import RespondentGroup, Respondent
from django.utils import timezone

@login_required
@require_http_methods(["POST"])
def create_respondent_group(request):
    # Get filter parameters from session or request
    gender = request.GET.get('gender')
    education = request.GET.get('education')
    employment = request.GET.get('employment')
    race = request.GET.get('race')
    country = request.GET.get('country')
    job_function = request.GET.get('job_function')
    job_industry = request.GET.get('job_industry')
    job_level = request.GET.get('job_level')
    company_size = request.GET.get('company_size')
    
    # Get group name from POST data
    group_name = request.POST.get('group_name', f'Group-{timezone.now().strftime("%Y%m%d%H%M%S")}')
    
    # Fetch all respondents and apply filters (same logic as in profiling view)
    all_respondents = Respondent.objects.all()
    filtered_respondents = []
    
    for respondent in all_respondents:
        # Profile completeness check
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
            continue
        
        # Apply filters
        if gender and respondent.gender != gender:
            continue
        if education and respondent.education != education:
            continue
        if employment and respondent.employment != employment:
            continue
        if race and respondent.race != race:
            continue
        if country and respondent.country != country:
            continue
        if job_function and respondent.job_function != job_function:
            continue
        if job_industry and respondent.job_industry != job_industry:
            continue
        if job_level and respondent.job_level != job_level:
            continue
        if company_size and respondent.company_size != company_size:
            continue
        
        filtered_respondents.append(respondent)
    
    # Create the group
    try:
        group = RespondentGroup.objects.create(
            name=group_name, 
            description=f'Group created from filtered respondents',
            created_by=request.user
        )
        
        # Add respondents to the group
        group.respondents.add(*filtered_respondents)
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Group "{group_name}" created with {len(filtered_respondents)} respondents',
            'group_id': group.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@login_required
def manage_groups(request):
    from respondent_app.models import RespondentGroup
    
    # Get all groups created by the current user
    groups = RespondentGroup.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Prepare context with group details
    group_details = []
    for group in groups:
        group_details.append({
            'id': group.id,
            'name': group.name,
            'description': group.description or 'No description',
            'created_at': group.created_at,
            'respondent_count': group.respondents.count()
        })
    
    context = {
        'groups': group_details,
        'title': 'Manage Respondent Groups'
    }
    
    return render(request, 'surveyapp/manage_groups.html', context)

@login_required
@require_http_methods(["POST"])
def delete_group(request, group_id):
    from respondent_app.models import RespondentGroup
    
    try:
        group = get_object_or_404(RespondentGroup, id=group_id, created_by=request.user)
        group.delete()
        return JsonResponse({'status': 'success', 'message': 'Group deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def group_details(request, group_id):
    from respondent_app.models import RespondentGroup
    
    # Get the group, ensuring it belongs to the current user
    group = get_object_or_404(RespondentGroup, id=group_id, created_by=request.user)
    
    # Prepare respondent details
    respondents = group.respondents.select_related('user').all()
    respondent_details = []
    
    for respondent in respondents:
        respondent_details.append({
            'id': respondent.id,
            'username': respondent.user.username,
            'full_name': f"{respondent.user.first_name} {respondent.user.last_name}".strip() or respondent.user.username,
            'email': respondent.user.email,
            'mobile': respondent.mobile or 'N/A',
            'gender': respondent.gender or 'N/A',
            'education': respondent.education or 'N/A',
            'employment': respondent.employment or 'N/A',
            'job_function': respondent.job_function or 'N/A',
            'job_industry': respondent.job_industry or 'N/A',
        })
    
    context = {
        'group': {
            'id': group.id,
            'name': group.name,
            'description': group.description or 'No description',
            'created_at': group.created_at,
            'created_by': group.created_by.username,
        },
        'respondents': respondent_details,
        'title': f'Group Details: {group.name}'
    }
    
    return render(request, 'surveyapp/group_details.html', context)

@login_required
@require_http_methods(["POST"])
def remove_respondent_from_group(request, group_id, respondent_id):
    from respondent_app.models import RespondentGroup, Respondent
    
    try:
        group = get_object_or_404(RespondentGroup, id=group_id, created_by=request.user)
        respondent = get_object_or_404(Respondent, id=respondent_id)
        
        # Remove the respondent from the group
        group.respondents.remove(respondent)
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Respondent removed from group successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)





from respondent_app.models import Respondent
from .visualizations import (
    generate_demographic_pie_chart,
    generate_education_bar_chart,
    generate_age_distribution
)

def dashboard(request):
    respondents = Respondent.objects.all()

    context = {
        'total_respondents': respondents.count(),
        'gender_chart': generate_demographic_pie_chart(respondents),
        'education_chart': generate_education_bar_chart(respondents),
        'age_chart': generate_age_distribution(respondents)
    }
    return render(request, 'surveyapp/dashboard.html', context)


   

from .models import Poll, PollChoice, PollResponse

@login_required
def create_poll(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        choices = request.POST.getlist('choices[]')
        expires_at = request.POST.get('expires_at')
        
        if question and choices:
            poll = Poll.objects.create(
                user=request.user,
                question=question,
                expires_at=expires_at if expires_at else None
            )
            
            # Create choices
            for choice_text in choices:
                if choice_text.strip():  # Only create non-empty choices
                    PollChoice.objects.create(
                        poll=poll,
                        choice_text=choice_text.strip()
                    )
            
            messages.success(request, 'Poll created successfully!')
            return redirect('poll_detail', poll_id=poll.id)
    
    return render(request, 'surveyapp/create_poll.html')

@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    total_votes = sum(choice.votes for choice in poll.choices.all())
    
    context = {
        'poll': poll,
        'total_votes': total_votes,
    }
    return render(request, 'surveyapp/poll_detail.html', context)

@login_required
def poll_list(request):
    polls = Poll.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'polls': polls
    }
    return render(request, 'surveyapp/poll_list.html', context)

@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if choice_id:
            choice = get_object_or_404(PollChoice, id=choice_id)
            
            # Check if user has already voted
            if not PollResponse.objects.filter(poll=poll, respondent=request.user).exists():
                PollResponse.objects.create(
                    poll=poll,
                    respondent=request.user,
                    choice=choice
                )
                choice.votes += 1
                choice.save()
                messages.success(request, 'Your vote has been recorded!')
            else:
                messages.error(request, 'You have already voted on this poll!')
                
        return redirect('poll_detail', poll_id=poll.id)
    
    context = {
        'poll': poll
    }
    return render(request, 'surveyapp/vote_poll.html', context)

@login_required
def share_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Get all respondents and share the poll with them
    all_respondents = User.objects.all().exclude(id=request.user.id)  # Exclude the poll creator
    poll.respondents.add(*all_respondents)
    
    messages.success(request, 'Poll shared with all respondents successfully!')
    return redirect('poll_detail', poll_id=poll.id)

@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, user=request.user)
    poll.delete()
    messages.success(request, 'Poll deleted successfully.')
    return redirect('poll_list')