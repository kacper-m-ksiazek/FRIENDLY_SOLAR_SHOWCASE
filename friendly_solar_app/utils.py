import joblib
import math as mh
import numpy as np
import pandas as pd
import pytz
import requests
import scipy.stats as stats
from datetime import datetime, time


def predict_location(latitude, longitude, days=7):
    """
    Predict solar radiation for a given location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        days (int): Number of days to predict. Default is 7.

    Returns:
        pandas.DataFrame: Solar radiation predictions.
    """
    timezone_name = get_timezone_name(latitude, longitude)
    time_zone = get_utc_offset(timezone_name)

    results = generate_many_years(time_zone, longitude, latitude, 1, 3, days=days)
    power, air_mass, elevation, azimuth = results

    return power, air_mass, elevation, azimuth


def get_timezone_name(latitude, longitude):
        """
    Retrieve the timezone name for a given location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        str: Timezone name.
    """
    tf = TimezoneFinder()
    return tf.timezone_at(lng=longitude, lat=latitude)


def get_utc_offset(timezone_name):
    """
    Retrieve the UTC offset for a given timezone.

    Args:
        timezone_name (str): Timezone name.

    Returns:
        float: UTC offset.
    """
    tm_now = datetime.now(pytz.timezone(timezone_name))
    return tm_now.utcoffset().total_seconds() / 3600


def generate_many_years(time_zone, longitude, latitude, years, counter, days=0):
    """
    Generate solar data for multiple years.

    Args:
        time_zone (float): Timezone offset.
        longitude (float): Longitude of the location.
        latitude (float): Latitude of the location.
        years (int): Number of years to generate data for.
        counter (int): Leap year counter.
        days (int): Number of days to generate data for. Default is 0 (all days).

    Returns:
        list: Solar data.
    """
    # Check if the current year is a leap year
    is_leap = datetime.now().year % 4 == 0 and (datetime.now().year % 100 != 0 or datetime.now().year % 400 == 0)

    results = []
    for year in range(years):
        if counter == 4:
            is_leap = not is_leap  # Switch leap year status every 4 years
            counter = 0

        days_in_year = 366 if is_leap else 365

        # Generate solar data for each day of the year
        for day_of_year in range(days_in_year):
            # Calculate solar data for the current day
            solar_data = generate_solar_data(day_of_year, time_zone, longitude, latitude)
            results.append(solar_data)

        counter += 1

    # If specified, slice the results to include only the specified number of days
    if days != 0:
        results = results[:days*24]

    return results


def generate_solar_data(day_of_year, time_zone, longitude, latitude):
        """
    Generate solar data for a single day.

    Args:
        day_of_year (int): Day of the year.
        time_zone (float): Timezone offset.
        longitude (float): Longitude of the location.
        latitude (float): Latitude of the location.

    Returns:
        tuple: Solar data.
    """
    irradiance = calculate_irradiance(day_of_year)
    declination_angle = calculate_declination_angle(day_of_year)
    power_daily = []
    air_mass_daily = []
    elevation_angle_daily = []
    azimuth_daily = []

    for local_time in range(24):
        # Calculate local solar time
        local_solar_time = calculate_local_solar_time(local_time, time_zone, longitude)
        # Calculate solar parameters for the current hour
        elevation_angle, azimuth, air_mass = calculate_solar_parameters(
            declination_angle, latitude, local_solar_time)
        
        # Store calculated parameters for each hour of the day
        power_daily.append(irradiance)
        air_mass_daily.append(air_mass)
        elevation_angle_daily.append(elevation_angle)
        azimuth_daily.append(azimuth)

    return power_daily, air_mass_daily, elevation_angle_daily, azimuth_daily


def calculate_irradiance(day_of_year):
    """Calculate solar irradiance for a given day of the year."""
    irradiance = (1 + 0.033 * mh.cos(2 * mh.pi * (day_of_year - 4) / 365)) * 1.366
    return round(irradiance, 4)


def calculate_declination_angle(day_of_year):
    """Calculate declination angle for a given day of the year."""
    declination_angle = 23.45 * mh.sin(mh.radians(360/365 * (day_of_year + 284)))
    return declination_angle


def calculate_local_solar_time(local_time, time_zone, longitude):
    """Calculate local solar time for a given hour."""
    local_solar_time = local_time + (4 * (longitude - 15 * time_zone) - calculate_equation_of_time(day_of_year)) / 60
    return local_solar_time


def calculate_equation_of_time(day_of_year):
    """Calculate the equation of time."""
    B = 360 / 365 * (day_of_year - 81)
    equation_of_time = 9.87 * mh.sin(mh.radians(2 * B)) - 7.53 * mh.cos(mh.radians(B)) - 1.5 * mh.sin(mh.radians(B))
    return equation_of_time


def calculate_solar_parameters(declination_angle, latitude, local_solar_time):
    """Calculate solar parameters for a given hour."""
    HRA = 15 * (local_solar_time - 12)
    elevation_angle = mh.degrees(mh.asin((mh.sin(mh.radians(declination_angle)) * mh.sin(mh.radians(latitude))
                                   + mh.cos(mh.radians(declination_angle)) * mh.cos(mh.radians(latitude))
                                   * mh.cos(mh.radians(HRA)))))
    air_mass = 1 / (mh.cos(mh.radians(90 - elevation_angle)) + 0.50572 * ((96.07995 - (90 - elevation_angle))**(-1.6364)))
    azimuth = mh.degrees(mh.acos((mh.sin(mh.radians(declination_angle)) * mh.cos(mh.radians(latitude))
                          - mh.cos(mh.radians(declination_angle)) * mh.sin(mh.radians(latitude))
                          * mh.cos(mh.radians(HRA))) / mh.cos(mh.radians(elevation_angle))))
    return elevation_angle, azimuth, air_mass


def predict_location(latitude, longitude, days):
    """Predict solar data for a location over a specified number of days."""
    response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=" + str(latitude) + "&longitude=" + 
str(longitude) + "&hourly=direct_radiation&forecast_days=" + 
str(days) + "&timezone=auto")

    response_json = response.json()
    data = pd.DataFrame(response_json['hourly'])
    
    """for the purposes of the demonstration, the exact implementation of the data processing and the use of an ensemble of hybrid neural network models for irradiance prediction have been hidden"""

    return data
