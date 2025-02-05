from django.urls import path
from .views import respondent_dashboard, complete_respondent_profile

app_name = 'respondent_app'

urlpatterns = [
    path('dashboard/', respondent_dashboard, name='dashboard'),
    path('complete_profile/', complete_respondent_profile, name='complete_profile'),
]