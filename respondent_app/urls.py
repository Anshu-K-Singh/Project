from django.urls import path
from .views import respondent_dashboard, complete_respondent_profile, take_poll

app_name = 'respondent_app'

urlpatterns = [
    path('dashboard/', respondent_dashboard, name='dashboard'),
    path('complete_profile/', complete_respondent_profile, name='complete_profile'),
    path('take_poll/<int:poll_id>/', take_poll, name='take_poll'),

]