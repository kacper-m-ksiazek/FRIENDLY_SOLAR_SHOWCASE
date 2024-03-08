from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from myapp.models import UserProfile
from .models import WeeklyPlanner, Appliance
from .forms import ApplianceForm, UserProfileForm
import json
from . import utils
import pandas as pd
import requests

def calculate(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude and longitude:  
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError as e:
                print("ValueError:", e)
                return HttpResponse("Latitude and/or longitude are invalid.", status=400)
        else:
            print("Latitude and/or longitude are empty or not provided.")
            return HttpResponse("Latitude and/or longitude are required.", status=400)
            
        days = 7
        predictions = utils.predict_location(latitude, longitude, days)
        result = list(zip(predictions["time"].tolist(), predictions["direct_normal_irradiance"].tolist()))

        return display_result(request, result)
    
    return render(request, 'calculate.html')

def display_result(request, result):
    result_data = [{'time': time, 'irradiance': irradiance} for time, irradiance in result]
    data_json = json.dumps(result_data)
    context = {'data_json': data_json}
    return render(request, 'result.html', context)

@login_required
def user_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse("Form data is invalid.", status=400)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'user_profile.html', {'profile': profile, 'form': form})

@login_required
def add_float_numbers(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  
        else:
            return HttpResponse("Form data is invalid.", status=400)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'add_coordinates.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('calculate')

@login_required
def view_weekly_planner(request):
    user = request.user
    predictions = WeeklyPlanner.objects.filter(user=user)
    appliances = Appliance.objects.filter(user=user) 
    return render(request, 'view_weekly_planner.html', {'predictions': predictions, 'appliances': appliances} )

def create_appliance(request):
    if request.method == 'POST':
        form = ApplianceForm(request.POST)
        if form.is_valid():
            appliance = form.save(commit=False)
            appliance.user = request.user
            appliance.save()
            return redirect('view_weekly_planner')
        else:
            return HttpResponse("Form data is invalid.", status=400)
    else:
        form = ApplianceForm()
    return render(request, 'create_appliance.html', {'form': form})

@login_required
def add_appliance_to_weekly_planner(request):
    if request.method == 'POST':
        weekly_planner_id = request.POST.get('weekly_planner')
        appliance_id = request.POST.get('appliance')
        
        try:
            weekly_planner = WeeklyPlanner.objects.get(id=weekly_planner_id, user=request.user)
            appliance = Appliance.objects.get(id=appliance_id, user=request.user)
            weekly_planner.appliances.add(appliance)
            return redirect('view_weekly_planner')
        except (WeeklyPlanner.DoesNotExist, Appliance.DoesNotExist):
            return HttpResponse("Weekly planner or appliance not found.", status=404)
    
    return redirect('view_weekly_planner')

@login_required
def add_panel_surface(request):
    if request.method == 'POST':
        panel_surface = request.POST.get('panel_surface')
        azimuth = request.POST.get('azimuth')
        elevation = request.POST.get('elevation')
        
        if panel_surface and azimuth and elevation:
            try:
                panel_surface = float(panel_surface)
                azimuth = float(azimuth)
                elevation = float(elevation)
            except ValueError as e:
                print("ValueError:", e)
                return HttpResponse("Panel surface, azimuth, or elevation is invalid.", status=400)
            
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.panel_surface = panel_surface
            user_profile.azimuth = azimuth
            user_profile.elevation = elevation
            user_profile.save()
            return redirect('user_profile')
        else:
            return HttpResponse("Panel surface, azimuth, and elevation are required.", status=400)
    
    return render(request, 'add_panel_surface.html')

@login_required
def calculate_savings(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponse("User profile not found.", status=404)

    latitude = user_profile.latitude
    longitude = user_profile.longitude

    energy_price = 0.00067
    panel_efficiency = 0.2

    year_start = 2010
    year_end = 2022

    years = year_end - year_start + 1

    api_request = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={year_start}-01-01&end_date={year_end}-12-31&hourly=direct_normal_irradiance&models=best_match&timezone=auto"

    try:
        response = requests.get(api_request)
        response_json = response.json()
        data = pd.DataFrame(response_json['hourly'])

        target = "direct_normal_irradiance"

        irradiance_mean = data[target].mean()

        expected_irradiance_yearly = irradiance_mean * 365 * 24

        expected_irradiance_yearly = expected_irradiance_yearly + expected_irradiance_yearly * 0.315

        savings = expected_irradiance_yearly * energy_price * panel_efficiency

        expected_irradiance_yearly_kW = expected_irradiance_yearly * 0.001

        azimuth = 180 if latitude > 0 else 0
        elevation = latitude

        context = {
            'irradiance': expected_irradiance_yearly_kW,
            'savings': savings,
            'azimuth': azimuth,
            'elevation': elevation
        }
    
        return render(request, 'calculate_savings.html', context)
    
    except Exception as e:
        print("Error calculating savings:", e)
        return HttpResponse("Error calculating savings.", status=500)
