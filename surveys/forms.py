from django import forms
from django.core.exceptions import ValidationError
from .models import Survey, Question, Choice

class ChoiceForm(forms.ModelForm):
    text = forms.CharField(
        label='Choice',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Enter choice text'
        })
    )

    class Meta:
        model = Choice
        fields = ['text']

class QuestionForm(forms.ModelForm):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('multiple_choice', 'Multiple Choice'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]

    text = forms.CharField(
        label='Question Text',
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Enter question text'
        })
    )

    question_type = forms.ChoiceField(
        choices=QUESTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'onchange': 'toggleChoices(this)'
        })
    )

    choices = forms.CharField(
        label='Choices',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Enter choices, one per line',
            'rows': 3
        })
    )

    class Meta:
        model = Question
        fields = ['text', 'question_type']

    def clean_choices(self):
        question_type = self.cleaned_data.get('question_type')
        choices = self.cleaned_data.get('choices', '').strip()

        if question_type in ['multiple_choice', 'checkbox', 'radio']:
            if not choices:
                raise ValidationError("Choices are required for Multiple Choice, Checkbox, and Radio questions.")
            
            # Split choices and remove empty lines
            choice_list = [choice.strip() for choice in choices.split('\n') if choice.strip()]
            
            if len(choice_list) < 2:
                raise ValidationError("At least two choices are required for Multiple Choice, Checkbox, and Radio questions.")
            
            if len(choice_list) > 10:
                raise ValidationError("Maximum 10 choices are allowed.")
            
            return choice_list
        return None

class SurveyForm(forms.ModelForm):
    title = forms.CharField(
        label='Survey Title',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Enter survey title'
        })
    )

    description = forms.CharField(
        label='Survey Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Optional survey description',
            'rows': 3
        })
    )

    class Meta:
        model = Survey
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError("Survey title must be at least 5 characters long.")
        return title
