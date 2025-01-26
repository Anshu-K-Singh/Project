from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SignUpTrend, UserDemographic, UserInsight, UserSource

# Register models in the admin interface
admin.site.register(SignUpTrend)
admin.site.register(UserDemographic)
admin.site.register(UserInsight)
admin.site.register(UserSource)
