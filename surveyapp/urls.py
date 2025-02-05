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
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'your_app_name.views.custom_404_view'
