"""friendly_solar_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import LoginView, LogoutView, SignupView, PasswordChangeView, PasswordSetView, PasswordResetView, PasswordResetDoneView, EmailView, ConfirmEmailView

from django.contrib import admin
from django.urls import include, path
from friendly_solar_app.views import calculate, display_result, user_profile, custom_logout, add_float_numbers, view_weekly_planner, create_appliance, add_appliance_to_weekly_planner, add_panel_surface, calculate_savings

from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('calculate'), name='root'),
    path("admin/", admin.site.urls),
    path('calculate/', calculate, name='calculate'),
    path('result/', display_result, name='result'),
    path('accounts/', include('allauth.urls')),
    path('accounts/login/', LoginView.as_view(), name='account_login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/signup/', SignupView.as_view(), name='signup'),
    path('accounts/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password/set/', PasswordSetView.as_view(), name='password_set'),
    path('accounts/password/reset', PasswordResetView.as_view(), name='password_reset'),
    path('accounts/email/', EmailView.as_view(), name='email'),
    path('accounts/confirm-email/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('accounts/profile/', user_profile, name='user_profile'),
    path('accounts/profile/coordinates/', add_float_numbers, name='add_coordinates'),
    path('accounts/profile/add-panel-surface/', add_panel_surface, name='add_panel_surface'),
    path('accounts/profile/view-weekly-planner/', view_weekly_planner, name='view_weekly_planner'),
    path('accounts/profile/add_appliance_to_weekly_planner/', add_appliance_to_weekly_planner, name='add_appliance_to_weekly_planner'),
    path('accounts/profile/calculate-savings/', calculate_savings, name='calculate_savings'),
    path('create_appliance/', create_appliance, name='create_appliance'),
    path('accounts/logout/', custom_logout, name='logout'),
    
]
