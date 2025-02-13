from django.db import models
from django.conf import settings

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

class Poll(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    respondents = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='polls', blank=True)

    def __str__(self):
        return self.question

class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    choice = models.ForeignKey(PollChoice, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['poll', 'respondent']

    def __str__(self):
        return f"{self.respondent} - {self.poll}"