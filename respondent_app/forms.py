from django import forms
from .models import Respondent

class RespondentProfileForm(forms.ModelForm):
    class Meta:
        model = Respondent
        fields = [
            'mobile', 'dob', 'gender', 'zipcode', 
            'education', 'employment', 'race', 
            'job_title', 'country', 'city', 'address', 
            'company', 'company_size', 'job_function', 
            'job_industry', 'job_level'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }