from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from a_resume.models import UserProfile

# Test constants
TEST_PASSWORD = "testpass123"  # nosec B105


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_page_loads(self):
        """Test that the registration page loads correctly"""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_user_registration(self):
        """Test user registration functionality"""
        data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": TEST_PASSWORD,
            "password2": TEST_PASSWORD,
            "terms": "on",
        }

        response = self.client.post(reverse("register"), data)

        # Check if user was created
        self.assertTrue(User.objects.filter(username="testuser").exists())

        # Check if user profile was created
        user = User.objects.get(username="testuser")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        # Check if redirect happened
        self.assertEqual(response.status_code, 302)

    def test_login_after_registration(self):
        """Test that user can login after registration"""
        # First register a user
        User.objects.create_user(
            username="testuser2", password=TEST_PASSWORD, email="test2@example.com"
        )

        # Try to login
        response = self.client.post(
            reverse("login"), {"username": "testuser2", "password": TEST_PASSWORD}
        )

        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))
