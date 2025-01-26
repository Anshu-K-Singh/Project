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

            # Handle the 'next' parameter, redirect to it after login, default to 'home'
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)  # Redirect to the next page after login
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
            return redirect('home')  # Redirect to home after successful registration
        else:
            messages.error(request, "There was an error with your registration. Please try again.")
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
