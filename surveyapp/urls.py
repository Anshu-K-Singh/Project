from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  
    path('home/', views.home, name='home'),  
    path('dashboarddata/', views.mdashboard, name='dashboarddata'),  
    path('fetch_table_data/', views.fetch_table_data, name='fetch_table_data'), 
    path('affiliate/', views.affiliate_view, name='affiliate'),
    path('surveymonitor/', views.survey_monitor, name='surveymonitor'),
    path('addsurvey/', views.add_survey, name='addsurvey'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('responseform/<int:survey_id>/', views.response_form, name='responseform'), 
    path('responseform/', views.response_form, name='responseform'), 
    path('survey/details/', views.survey_details, name='surveydetails'),
    path('survey/deactivate/', views.deactivate_survey, name='deactivate_survey'),
    path('submit_survey/', views.submit_survey, name='submit_survey'),
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'your_app_name.views.custom_404_view'
