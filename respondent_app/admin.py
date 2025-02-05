from django.contrib import admin
from .models import Respondent
# Register your models here.
class RespondentAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'dob', 'gender', 'zipcode', 'education', 'employment', 'race', 'job_title', 'country', 'city', 'address', 'company', 'company_size', 'job_function', 'job_industry', 'job_level')
    list_filter = ('gender', 'education', 'employment', 'race', 'country', 'company_size', 'job_function', 'job_industry', 'job_level')

admin.site.register(Respondent, RespondentAdmin)
