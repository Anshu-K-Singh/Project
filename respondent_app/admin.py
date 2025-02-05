from django.contrib import admin
from .models import Respondent, RespondentGroup
# Register your models here.
class RespondentAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'dob', 'gender', 'zipcode', 'education', 'employment', 'race', 'job_title', 'country', 'city', 'address', 'company', 'company_size', 'job_function', 'job_industry', 'job_level')
    list_filter = ('gender', 'education', 'employment', 'race', 'country', 'company_size', 'job_function', 'job_industry', 'job_level')

class RespondentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by', 'created_at')
    search_fields = ('name', 'description')

admin.site.register(Respondent, RespondentAdmin)
admin.site.register(RespondentGroup, RespondentGroupAdmin)
