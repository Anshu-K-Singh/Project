from django.urls import path
from .views import respondent_dashboard, complete_respondent_profile, take_poll, edit_profile, survey_history, delete_survey_history, survey_wall

app_name = 'respondent_app'

urlpatterns = [
    path('dashboard/', respondent_dashboard, name='dashboard'),
    path('complete_profile/', complete_respondent_profile, name='complete_profile'),
    path('take_poll/<int:poll_id>/', take_poll, name='take_poll'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('survey_history/', survey_history, name='survey_history'),
    path('delete_survey_history/<int:response_id>/', delete_survey_history, name='delete_survey_history'),
    path('survey_wall/', survey_wall, name='survey_wall'),

]