import numpy as np
import pandas as pd
from . import utils
from datetime import datetime, time
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from sklearn.preprocessing import StandardScaler
from timezonefinder import TimezoneFinder
from .models import UserProfile, WeeklyPlanner


def create_user_profile(sender, instance, created, **kwargs):
        """
    Create a user profile when a new account is created.

    Args:
        sender: The sender of the signal.
        instance: The instance being saved.
        created (bool): Indicates whether the instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        UserProfile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
        """
    Save the user profile after each update.

    Args:
        sender: The sender of the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.
    """
    instance.userprofile.save()


def generate_and_update_predictions(sender, request, user, **kwargs):
       """
    Generate and update predictions based on user's location.

    Args:
        sender: The sender of the signal.
        request: The request object.
        user: The user object.
        **kwargs: Additional keyword arguments.
    """
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return

    try:
        latitude = profile.latitude
        longitude = profile.longitude
        days = 7

        predictions_data = utils.predict_location(latitude, longitude, days)

        for _, row in predictions_data.iterrows():
            date_str = row["time"]
            date = convert_to_date(date_str)
            hour = convert_to_hour(date_str)
            hourly_predictions = row["direct_radiation"]
            azimuth = row["azimuth"]
            elevation = row["elevation"]
            try:
                weekly_planner = WeeklyPlanner.objects.get(date=date, hour=hour, user=user)
                weekly_planner.predictions = hourly_predictions
                weekly_planner.azimuth = azimuth
                weekly_planner.elevation = elevation
                weekly_planner.save()
            except WeeklyPlanner.DoesNotExist:
                WeeklyPlanner.objects.create(user=user, date=date, hour=hour,
                                             predictions=hourly_predictions, azimuth=azimuth, elevation=elevation)
    except Exception as e:
        print("Error:", e)


def update_weekly_planner(user, predictions):
    """Update the weekly planner for a given user."""
    power, _, elevation, azimuth = predictions

    for idx, (date_str, hourly_predictions) in enumerate(power.iteritems()):
        date = convert_to_date(date_str)
        hour = convert_to_hour(date_str)

        try:
            weekly_planner = WeeklyPlanner.objects.get(date=date, hour=hour, user=user)
            weekly_planner.predictions = hourly_predictions
            weekly_planner.azimuth = azimuth[idx]
            weekly_planner.elevation = elevation[idx]
            weekly_planner.save()
        except WeeklyPlanner.DoesNotExist:
            WeeklyPlanner.objects.create(
                user=user,
                date=date,
                hour=hour,
                predictions=hourly_predictions,
                azimuth=azimuth[idx],
                elevation=elevation[idx]
            )


def convert_to_date(date_str):
    """Convert a string to a date object."""
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M").date()


def convert_to_hour(date_str):
    """Convert a string to a time object."""
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M").time()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Signal to create or update a user profile."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


@receiver(user_logged_in)
def generate_and_update_predictions_on_login(sender, request, user, **kwargs):
    """Signal triggered upon user login."""
    generate_and_update_predictions(sender, request, user, **kwargs)
