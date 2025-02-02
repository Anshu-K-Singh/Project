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
