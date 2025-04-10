from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('home/', views.home, name='home'),  
    path('dashboarddata/', views.mdashboard, name='dashboarddata'),  
    path('fetch_table_data/', views.fetch_table_data, name='fetch_table_data'), 
    path('affiliate/', views.affiliate_view, name='affiliate'),
    path('surveymonitor/', views.monitorsurvey, name='surveymonitor'),
    path('profiling/', views.profiling, name='profiling'),
    path('profiling/respondent/<int:respondent_id>/', views.get_respondent_details, name='respondent_details'),
    path('profiling/respondent/<int:respondent_id>/delete/', views.delete_respondent, name='delete_respondent'),
    path('profiling/create-group/', views.create_respondent_group, name='create_respondent_group'),
    path('profiling/manage-groups/', views.manage_groups, name='manage_groups'),
    path('profiling/delete-group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('profiling/group/<int:group_id>/', views.group_details, name='group_details'),
    path('profiling/group/<int:group_id>/remove-respondent/<int:respondent_id>/', 
         views.remove_respondent_from_group, name='remove_respondent_from_group'),
    # path('dashboard/chart/', views.load_respondent_chart, name='load_chart'),
    # path("debug-chart-data/", views.debug_chart_data, name="debug-chart-data"),

    # Poll URLs
    path('polls/', views.poll_list, name='poll_list'),
    path('polls/create/', views.create_poll, name='create_poll'),
    path('polls/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
    path('polls/<int:poll_id>/share/', views.share_poll, name='share_poll'),
    path('polls/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),

    # Move this before other patterns to ensure it's matched correctly
    path('survey-click/<int:survey_id>/', views.increment_survey_click, name='increment_survey_click'),

    # QR Code Generation URL
    path('survey/<int:survey_id>/qr-code/', views.generate_survey_qr_code, name='survey_qr_code'),
    path('news/', views.news_page, name='news'),
    path('support/', views.support_page, name='support'),
    path('submit-support-query/', views.submit_support_query, name='submit_support_query'),
    path('chatbot/', views.chatbot_response, name='chatbot_response'),
    path('survey-host/', views.SurveyHostView.as_view(), name='survey_host'),
    path('delete-hosted-survey/<int:survey_id>/', views.delete_hosted_survey, name='delete_hosted_survey'),
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'your_app_name.views.custom_404_view'
