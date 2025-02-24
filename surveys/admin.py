from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from .models import Survey, SurveyPage, Question, Choice, Answer, Response, SurveyDistribution, SurveyNotification
from unfold.admin import ModelAdmin  # Unfold's UI for Django Admin

# Create Import/Export Resources
class SurveyResource(ModelResource):
    class Meta:
        model = Survey

class QuestionResource(ModelResource):
    class Meta:
        model = Question

class ChoiceResource(ModelResource):
    class Meta:
        model = Choice

class AnswerResource(ModelResource):
    class Meta:
        model = Answer

class ResponseResource(ModelResource):
    class Meta:
        model = Response

class SurveyPageResource(ModelResource):
    class Meta:
        model = SurveyPage

# Inline for Choices in Questions
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

# Survey Admin
@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin, ModelAdmin):  
    resource_class = SurveyResource
    list_display = ('title', 'user', 'created_at', 'is_active', 'is_expired')
    list_editable = ('is_active',)
    fields = ('title', 'description', 'user', 'expiry_datetime', 'is_active')
    readonly_fields = ('created_at', 'unique_link', 'external_link', 'external_response_count')
    list_filter = ('created_at', 'is_active', 'is_expired')
    search_fields = ('title', 'user__username')
    list_per_page = 15
    date_hierarchy = 'created_at'  # Enables date-based filtering
    list_badges = {
        "is_active": {"True": "success", "False": "danger"},
        "is_expired": {"True": "danger", "False": "success"},
    }

# Survey Page Admin
@admin.register(SurveyPage)
class SurveyPageAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = SurveyPageResource
    list_display = ('title', 'survey', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'survey__title')
    list_filter = ('survey',)
    ordering = ('survey', 'order')

# Question Admin
@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = QuestionResource
    list_display = ('survey', 'text', 'question_type')
    list_filter = ('survey', 'question_type')
    search_fields = ('text', 'survey__title')
    list_per_page = 10
    inlines = [ChoiceInline]

# Choice Admin
@admin.register(Choice)
class ChoiceAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ChoiceResource
    list_display = ('question', 'text', 'is_eligibility_flag')
    list_editable = ('is_eligibility_flag',)
    list_filter = ('question',)
    search_fields = ('text',)

# Response Admin
@admin.register(Response)
class ResponseAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ResponseResource
    list_display = ('survey', 'user', 'submitted_at')
    readonly_fields = ('submitted_at',)
    list_filter = ('survey',)
    search_fields = ('survey__title', 'user__username')
    date_hierarchy = 'submitted_at'

# Answer Admin
@admin.register(Answer)
class AnswerAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = AnswerResource
    list_display = ('response', 'question', 'text_answer', 'choice_answer')
    list_filter = ('question',)
    search_fields = ('question__text',)

# Survey Distribution Admin
@admin.register(SurveyDistribution)
class SurveyDistributionAdmin(ModelAdmin):
    list_display = ('survey', 'group', 'sent_count', 'failed_count', 'created_at')
    list_filter = ('survey', 'group')
    search_fields = ('survey__title', 'group__name')
    readonly_fields = ('sent_count', 'failed_count', 'created_at')

# Survey Notification Admin
@admin.register(SurveyNotification)
class SurveyNotificationAdmin(ModelAdmin):
    list_display = ('survey', 'user', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('survey__title', 'user__username')
    readonly_fields = ('created_at',)
    list_badges = {"is_read": {"True": "success", "False": "danger"}}
