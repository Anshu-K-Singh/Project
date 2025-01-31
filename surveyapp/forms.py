from django import forms
from .models import Affiliate

# forms.py

class AffiliateForm(forms.ModelForm):
    class Meta:
        model = Affiliate
        fields = ['title', 'link', 'callback_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }