from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Create your models here.
class Respondent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    EDUCATION_CHOICES = [('High School Diploma', 'High School Diploma'), ('Bachelor\'s Degree', 'Bachelor\'s Degree'), ('Master\'s Degree', 'Master\'s Degree'), ('Doctoral Degree', 'Doctoral Degree'), ('Other', 'Other')]
    EMPLOYMENT_CHOICES = [('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Freelancer', 'Freelancer'), ('Unemployed', 'Unemployed'), ('Other', 'Other')]
    RACE_CHOICES = [('South Asian', 'South Asian'), ('Asian', 'Asian'), ('Black or African American', 'Black or African American'), ('Hispanic or Latino', 'Hispanic or Latino'), ('Native American or Alaska Native', 'Native American or Alaska Native'), ('White', 'White'), ('Other', 'Other')]
    COUNTRY_CHOICES = [('India', 'India'), ('United States', 'United States'), ('United Kingdom', 'United Kingdom'), ('Canada', 'Canada'), ('Australia', 'Australia'), ('Germany', 'Germany'), ('France', 'France')]
    COMPANY_SIZE_CHOICES = [('less than 10', 'less than 10'), ('10-50', '10-50'), ('50-100', '50-100'), ('100-500', '100-500'), ('500-1000', '500-1000'), ('more than 1000', 'more than 1000')]
    JOB_LEVEL_CHOICES = [('entry level', 'entry level'), ('mid level', 'mid level'), ('senior level', 'senior level'), ('executive', 'executive'), ('other', 'other')]
    JOB_FUNCTION_CHOICES = [('IT', 'IT'), ('Finance', 'Finance'), ('Marketing', 'Marketing'), ('Sales', 'Sales'), ('Operations', 'Operations'), ('HR', 'HR'), ('other', 'other')]
    JOB_INDUSTRY_CHOICES = [('Technology', 'Technology'), ('Finance', 'Finance'), ('Healthcare', 'Healthcare'), ('Retail', 'Retail'), ('Manufacturing', 'Manufacturing'), ('Energy', 'Energy'), ('other', 'other')]
    mobile = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)  # Date of Birth
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    education = models.CharField(max_length=100, choices=EDUCATION_CHOICES, null=True, blank=True)
    employment = models.CharField(max_length=100, choices=EMPLOYMENT_CHOICES, null=True, blank=True)
    race = models.CharField(max_length=100, choices=RACE_CHOICES, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    company_size = models.CharField(max_length=100, choices=COMPANY_SIZE_CHOICES, null=True, blank=True)
    job_function = models.CharField(max_length=100, choices=JOB_FUNCTION_CHOICES, null=True, blank=True)
    job_industry = models.CharField(max_length=100, choices=JOB_INDUSTRY_CHOICES, null=True, blank=True)
    job_level = models.CharField(max_length=100, choices=JOB_LEVEL_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"
