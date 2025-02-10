from django.urls import path
from .views import (
    HomeView,
    CreateSurveyView, 
    SurveyDetailView, 
    TakeSurveyView, 
    SurveyResultsView,
    ExportSurveyCSVView,
    DeactivateSurveyView,
    EditSurveyView,
    SurveyHistoryView,
    ExportSurveyPDFView,
    SendSurveyToGroupView
)

app_name = 'surveys'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateSurveyView.as_view(), name='create_survey'),
    path('survey/<int:survey_id>/', SurveyDetailView.as_view(), name='survey_detail'),
    path('take/<str:unique_link>/', TakeSurveyView.as_view(), name='take_survey'),
    path('survey/<int:survey_id>/results/', SurveyResultsView.as_view(), name='survey_results'),
    path('export-csv/<int:survey_id>/', ExportSurveyCSVView.as_view(), name='export_survey_csv'),
    path('deactivate/<int:survey_id>/', DeactivateSurveyView.as_view(), name='deactivate_survey'),
    path('survey/<int:survey_id>/edit/', EditSurveyView.as_view(), name='edit_survey'),
    path('survey/history/', SurveyHistoryView.as_view(), name='survey_history'),
    path('export-pdf/<int:survey_id>/', ExportSurveyPDFView.as_view(), name='export_survey_pdf'),
    path('survey/<int:survey_id>/send-to-group/', SendSurveyToGroupView.as_view(), name='send_survey_to_group'),
]
