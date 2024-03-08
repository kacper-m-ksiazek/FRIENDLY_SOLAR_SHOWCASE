from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from .models import UserProfile, Appliance, WeeklyPlanner

class UserProfileForm(forms.ModelForm):
    latitude = forms.DecimalField(
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = forms.DecimalField(
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    class Meta:
        model = UserProfile
        fields = ['latitude', 'longitude']


class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'energy_consumption']


