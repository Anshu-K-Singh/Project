from django.db import models

#
# Model for storing user sign-up trend
class SignUpTrend(models.Model):
    date = models.DateField()
    total_signups = models.IntegerField()

    def __str__(self):
        return f"Signups on {self.date}: {self.total_signups}"

# Model for storing user demographics
class UserDemographic(models.Model):
    user_id = models.IntegerField()
    age_group = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"User {self.user_id} | Age Group: {self.age_group}, Gender: {self.gender}, Location: {self.location}"

# Model for storing user insights
class UserInsight(models.Model):
    user_id = models.IntegerField()
    satisfaction_score = models.IntegerField()  # 1-5 scale
    feedback = models.TextField()

    def __str__(self):
        return f"User {self.user_id} | Satisfaction: {self.satisfaction_score}"

# Model for storing user sources
class UserSource(models.Model):
    user_id = models.IntegerField()
    source = models.CharField(max_length=100)  # Where the user came from (e.g., Referral, Social Media)

    def __str__(self):
        return f"User {self.user_id} | Source: {self.source}"



from django.db import models

class Affiliate(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    callback_url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.title





#MODELS FOR SURVEY MONITOR

class Surveymonitor(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    loi = models.PositiveIntegerField(blank=True, null=True)  # Length of Interview
    c = models.PositiveIntegerField(blank=True, null=True)   # Some integer field (clarify as needed)
    t = models.PositiveIntegerField(blank=True, null=True)   # Some integer field (clarify as needed)
    d = models.PositiveIntegerField(blank=True, null=True)   # Some integer field (clarify as needed)
    launch = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'Active', 'Inactive'
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Closed', 'Closed')],
        default='Inactive'
    )

    def __str__(self):
        return f"{self.code} - {self.name or 'Unnamed Survey'}"