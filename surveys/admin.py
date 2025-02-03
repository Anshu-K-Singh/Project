from django.contrib import admin
from . models import Survey, Question, Choice, Answer, Response
# Register your models here.


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    fields = ('title', 'user')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'text', 'question_type')
    fields = ('survey', 'text', 'question_type')
    list_filter = ('question_type',)

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text')
    fields = ('question', 'text')
    list_filter = ('question',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'text_answer', 'choice_answer')
    fields = ('response', 'question', 'text_answer', 'choice_answer')
    list_filter = ('question',)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'submitted_at')
    fields = ('survey', 'submitted_at')
    list_filter = ('submitted_at',) 
