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
    path('surveymonitor/', views.survey_monitor, name='surveymonitor'),
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# handler404 = 'your_app_name.views.custom_404_view'
