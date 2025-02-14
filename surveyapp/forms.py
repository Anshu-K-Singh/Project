from django import forms
from .models import Affiliate, SupportQuery


# forms.py

class AffiliateForm(forms.ModelForm):
    class Meta:
        model = Affiliate
        fields = ['title', 'link', 'callback_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }




class SupportQueryForm(forms.ModelForm):
    class Meta:
        model = SupportQuery
        fields = ['name', 'email', 'query']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', 'id': 'id_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email', 'id': 'id_email'}),
            'query': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your issue', 'id': 'id_query'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name cannot be empty.")
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if not re.match(r'^[a-zA-Z\s]+$', name):
            raise forms.ValidationError("Name can only contain letters and spaces.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email cannot be empty.")
        
        # Use Django's built-in email validator
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except forms.ValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        return email

    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if not query:
            raise forms.ValidationError("Query cannot be empty.")
        if len(query) < 10:
            raise forms.ValidationError("Query must be at least 10 characters long.")
        return query