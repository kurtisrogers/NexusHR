from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from employees.models import Employee
from hrms.test_utils import create_user
from leave.models import LeaveRequest


class NexusHRTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user("testuser")

    def test_login_page_loads(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NexusHR")

    def test_dashboard_requires_auth(self):
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_dashboard(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_seed_demo_command(self):
        call_command("seed_demo")
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertGreater(Employee.objects.count(), 0)
        self.assertGreater(LeaveRequest.objects.count(), 0)


class UserModelTests(TestCase):
    def test_display_name_uses_full_name(self):
        user = create_user("jdoe", first_name="Jane", last_name="Doe")
        self.assertEqual(user.display_name, "Jane Doe")

    def test_display_name_falls_back_to_username(self):
        user = create_user("jdoe", first_name="", last_name="")
        self.assertEqual(user.display_name, "jdoe")

    def test_role_properties(self):
        hr_admin = create_user("hr", role=UserRole.HR_ADMIN)
        manager = create_user("mgr", role=UserRole.MANAGER)
        recruiter = create_user("rec", role=UserRole.RECRUITER)
        employee = create_user("emp", role=UserRole.EMPLOYEE)

        self.assertTrue(hr_admin.is_hr_staff)
        self.assertTrue(hr_admin.is_manager_or_above)
        self.assertTrue(hr_admin.can_recruit)

        self.assertFalse(manager.is_hr_staff)
        self.assertTrue(manager.is_manager_or_above)
        self.assertFalse(manager.can_recruit)

        self.assertFalse(recruiter.is_hr_staff)
        self.assertFalse(recruiter.is_manager_or_above)
        self.assertTrue(recruiter.can_recruit)

        self.assertFalse(employee.is_hr_staff)
        self.assertFalse(employee.is_manager_or_above)
        self.assertFalse(employee.can_recruit)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.employee = create_user("employee")
        self.hr_admin = create_user("hr.admin", role=UserRole.HR_ADMIN)

    def test_employee_cannot_access_user_list(self):
        self.client.login(username="employee", password="testpass123")
        response = self.client.get(reverse("accounts:users"))
        self.assertEqual(response.status_code, 403)

    def test_hr_admin_can_access_user_list(self):
        self.client.login(username="hr.admin", password="testpass123")
        response = self.client.get(reverse("accounts:users"))
        self.assertEqual(response.status_code, 200)
