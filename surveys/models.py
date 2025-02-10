from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings

# Create your models here.

class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='surveys',
        null=True  # Allow existing surveys to remain
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_link = models.CharField(max_length=16, unique=True, blank=True)
    is_active = models.BooleanField(default=True)  # New field to track survey activation status
    
    def save(self, *args, **kwargs):
        if not self.unique_link:
            self.unique_link = get_random_string(length=16)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('multiple_choice', 'Multiple Choice'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]
    
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    
    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text

class Response(models.Model):
    survey = models.ForeignKey(Survey, related_name='responses', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='survey_responses', on_delete=models.CASCADE, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('survey', 'user')
    
    def __str__(self):
        return f"Response to {self.survey.title} by {self.user.username if self.user else 'Anonymous'} at {self.submitted_at}"

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    choice_answer = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"Answer to {self.question.text}"

class SurveyDistribution(models.Model):
    survey = models.ForeignKey(Survey, related_name='distributions', on_delete=models.CASCADE)
    group = models.ForeignKey('respondent_app.RespondentGroup', related_name='survey_distributions', on_delete=models.CASCADE)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Distribution of {self.survey.title} to {self.group.name}"
    
    class Meta:
        verbose_name_plural = "Survey Distributions"

class SurveyNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_notifications')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'survey')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.survey.title} to {self.user.username}"
