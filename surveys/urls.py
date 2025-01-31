from django.urls import path
from .views import (
    HomeView,
    CreateSurveyView, 
    SurveyDetailView, 
    TakeSurveyView, 
    SurveyResultsView,
    ExportSurveyCSVView
)

app_name = 'surveys'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateSurveyView.as_view(), name='create_survey'),
    path('survey/<int:survey_id>/', SurveyDetailView.as_view(), name='survey_detail'),
    path('take/<str:unique_link>/', TakeSurveyView.as_view(), name='take_survey'),
    path('survey/<int:survey_id>/results/', SurveyResultsView.as_view(), name='survey_results'),
    path('export-csv/<int:survey_id>/', ExportSurveyCSVView.as_view(), name='export_survey_csv'),
    
]
