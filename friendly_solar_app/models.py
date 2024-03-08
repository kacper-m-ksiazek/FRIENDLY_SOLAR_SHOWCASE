from django.contrib.auth.models import User
from django.db import models
import math


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True) 
    azimuth = models.FloatField(blank=True, null=True) 
    elevation = models.FloatField(blank=True, null=True) 
    panel_surface = models.FloatField(default=0.0, blank=True, null=True)
    panel_efficiency = models.FloatField(default=0.2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Panel Surface: {self.panel_surface}"


def get_admin_user():
    try:
        return User.objects.get(username='admin')
    except User.DoesNotExist:
        return None


class Appliance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    energy_consumption = models.FloatField(blank=True, null=True)
    is_public = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.name


class WeeklyPlanner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appliances = models.ManyToManyField(Appliance)
    date = models.DateField(default=None, null=True)
    hour = models.TimeField(default=None, null=True)
    predictions = models.FloatField(blank=True, null=True) 
    azimuth = models.FloatField(blank=True, null=True) 
    elevation = models.FloatField(blank=True, null=True) 
    
    def __str__(self):
        return f"{self.user.username} - {[appliance.name for appliance in self.appliances.all()] or 'None'} - Date: {self.date}"

    def get_total_energy_consumption(self):
        total_energy_consumption = 0.0
        for appliance in self.appliances.all():
            total_energy_consumption += appliance.energy_consumption
        return total_energy_consumption

    def get_energy_produced(self):
        if self.user.userprofile.panel_surface is not None and self.predictions is not None and self.user.userprofile.azimuth is not None and self.user.userprofile.elevation is not None:
            return self.predictions * self.user.userprofile.panel_surface * self.user.userprofile.panel_efficiency * abs(math.cos(math.radians(self.user.userprofile.azimuth) - math.radians(self.azimuth))) * abs(math.sin(math.radians(self.user.userprofile.elevation)) - math.radians(self.elevation)) + self.predictions* 0.315 * self.user.userprofile.panel_efficiency
        return None