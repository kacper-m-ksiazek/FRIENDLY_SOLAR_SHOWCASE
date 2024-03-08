from django.contrib import admin
from .models import WeeklyPlanner, Appliance, UserProfile

admin.site.register(WeeklyPlanner)
admin.site.register(Appliance)
admin.site.register(UserProfile)