from django import forms
from .models import Survey, Question
from .models import Affiliate

# forms.py

class AffiliateForm(forms.ModelForm):
    class Meta:
        model = Affiliate
        fields = ['title', 'link', 'callback_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['name', 'description']


class QuestionForm(forms.ModelForm):
    # To handle dynamic input like multiple choice and dropdown options, we'll use a method to clean choices.
    class Meta:
        model = Question
        fields = ['text', 'answer_type', 'choices', 'required']

    def clean_choices(self):
        # For multiple choice and dropdown, clean the choices field
        answer_type = self.cleaned_data.get('answer_type')
        choices = self.cleaned_data.get('choices')

        # Clean choices only if it's a multiple choice or dropdown
        if answer_type in ['multipleChoice', 'dropdown'] and choices:
            # Split the choices into a list
            choices_list = [choice.strip() for choice in choices.split(',')]
            return choices_list
        return choices