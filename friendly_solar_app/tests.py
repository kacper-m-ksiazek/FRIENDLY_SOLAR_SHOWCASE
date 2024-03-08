from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, WeeklyPlanner, Appliance
from .signals import generate_and_update_predictions, create_or_update_user_profile


class SignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.profile = UserProfile.objects.create(user=self.user, latitude=0.0, longitude=0.0)
        self.predictions_data = [
            {'time': '2024-03-07T07:00', 'direct_radiation': 100, 'azimuth': 180, 'elevation': 45},
            {'time': '2024-03-07T08:00', 'direct_radiation': 120, 'azimuth': 200, 'elevation': 50},
        ]

    def test_generate_and_update_predictions(self):
        # Mock the request object
        request = None
        # Trigger the signal handler
        generate_and_update_predictions(sender=None, request=request, user=self.user)
        # Check if WeeklyPlanner objects were created or updated as expected
        for data in self.predictions_data:
            date_str = data['time']
            date = convert_to_date(date_str)
            hour = convert_to_hour(date_str)
            weekly_planner = WeeklyPlanner.objects.get(date=date, hour=hour, user=self.user)
            self.assertEqual(weekly_planner.predictions, data['direct_radiation'])
            self.assertEqual(weekly_planner.azimuth, data['azimuth'])
            self.assertEqual(weekly_planner.elevation, data['elevation'])

    def test_create_or_update_user_profile(self):
        # Create a new user
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='newpassword')
        # Trigger the signal handler
        create_or_update_user_profile(sender=User, instance=new_user, created=True)
        # Check if a UserProfile object was created for the new user
        user_profile = UserProfile.objects.get(user=new_user)
        self.assertIsNotNone(user_profile)
        self.assertEqual(user_profile.user, new_user)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.profile = UserProfile.objects.create(user=self.user, latitude=0.0, longitude=0.0)

    def test_calculate_view(self):
        url = reverse('calculate')
        # Test GET request to calculate view
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST request to calculate view with valid data
        data = {'latitude': 0.0, 'longitude': 0.0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Assuming it returns a successful response

        # Test POST request to calculate view with missing data
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

    def test_user_profile_view(self):
        url = reverse('user_profile')
        # Test GET request to user_profile view
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST request to user_profile view with valid data
        data = {'latitude': 10.0, 'longitude': 20.0}  # Assuming UserProfileForm fields
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Assuming it returns a successful response

        # Test POST request to user_profile view with invalid data
        data = {'latitude': 'invalid', 'longitude': 'invalid'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Assuming it returns a successful response
        self.assertContains(response, "Invalid data")


