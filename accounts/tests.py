from django.test import Client, TestCase

from accounts.models import User, UserRole
from employees.models import Employee
from leave.models import LeaveRequest


class NexusHRTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role=UserRole.EMPLOYEE,
            first_name="Test",
            last_name="User",
        )

    def test_login_page_loads(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NexusHR")

    def test_dashboard_requires_auth(self):
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 302)

    def test_authenticated_dashboard(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 200)

    def test_seed_demo_command(self):
        from django.core.management import call_command

        call_command("seed_demo")
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertGreater(Employee.objects.count(), 0)
        self.assertGreater(LeaveRequest.objects.count(), 0)
