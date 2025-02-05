from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserRegisterForm



def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # If login is successful, authenticate and log the user in
            user = form.get_user()
            login(request, user)

            # Custom redirection logic
            if user.is_superuser:
                # Superusers go to home page
                return redirect('home')
            else:
                # Regular users go to respondent dashboard
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = AuthenticationForm()

    # Add cache control to the login page to prevent caching
    response = render(request, 'account_app/login.html', {'form': form})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the user and log them in
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully for {user.username}!")
            
            # Attempt to create a Respondent profile
            try:
                from respondent_app.models import Respondent
                # Check if a Respondent profile already exists
                respondent, created = Respondent.objects.get_or_create(user=user)
                
                # Always redirect to complete profile after registration
                return redirect('complete_profile')
            except Exception as e:
                messages.warning(request, f"Could not create respondent profile: {e}")
                return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'account_app/register.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)  # Log out the user and clear session data

    # Redirect to login page after logout
    response = redirect('login')

    # Add cache control headers to ensure that the page is not cached
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    # Clear session cookie explicitly
    response.delete_cookie('sessionid')

    return response

@login_required
def login_required_view(request):
    # If the user is not authenticated, redirect them to login
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{reverse("login")}?next={request.path}')

    # Continue with the view logic if authenticated
    return render(request, 'account_app/login_required.html')
