from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from a_resume.models import UserProfile

# Demo user credentials
DEMO_PASSWORD = "demo123"  # nosec B105
TEST_PASSWORD = "testpass123"  # nosec B105


class Command(BaseCommand):
    help = "Create demo users for testing"

    def handle(self, *args, **options):
        # Create demo regular user
        if not User.objects.filter(username="demo").exists():
            demo_user = User.objects.create_user(
                username="demo",
                password=DEMO_PASSWORD,
                email="demo@example.com",
                first_name="Demo",
                last_name="User",
            )
            UserProfile.objects.create(user=demo_user)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Demo user created: username=demo, password=demo123"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("Demo user already exists"))

        # Create test user
        if not User.objects.filter(username="testuser").exists():
            test_user = User.objects.create_user(
                username="testuser",
                password=TEST_PASSWORD,
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
            UserProfile.objects.create(user=test_user)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test user created: username=testuser, password=testpass123"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("Test user already exists"))

        self.stdout.write(self.style.SUCCESS("Demo users setup complete!"))
