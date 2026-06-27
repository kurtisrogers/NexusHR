from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from employees.models import Employee
from hrms.test_utils import create_hr_setup, create_user
from leave.models import LeaveRequest


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_page_loads(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NexusHR")

    def test_dashboard_requires_auth(self):
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_dashboard(self):
        create_user("dashuser")
        self.client.login(username="dashuser", password="testpass123")
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_to_login(self):
        create_user("logoutuser")
        self.client.login(username="logoutuser", password="testpass123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class UserModelTests(TestCase):
    def test_display_name_uses_full_name(self):
        user = create_user("named", first_name="Ada", last_name="Lovelace")
        self.assertEqual(user.display_name, "Ada Lovelace")

    def test_display_name_falls_back_to_username(self):
        user = User.objects.create_user(username="noname", password="x")
        self.assertEqual(user.display_name, "noname")

    def test_is_hr_staff(self):
        hr = create_user("hr", UserRole.HR_ADMIN)
        emp = create_user("e", UserRole.EMPLOYEE)
        self.assertTrue(hr.is_hr_staff)
        self.assertFalse(emp.is_hr_staff)

    def test_is_manager_or_above(self):
        mgr = create_user("m", UserRole.MANAGER)
        emp = create_user("e2", UserRole.EMPLOYEE)
        self.assertTrue(mgr.is_manager_or_above)
        self.assertFalse(emp.is_manager_or_above)

    def test_can_recruit(self):
        rec = create_user("r", UserRole.RECRUITER)
        emp = create_user("e3", UserRole.EMPLOYEE)
        self.assertTrue(rec.can_recruit)
        self.assertFalse(emp.can_recruit)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_hr_users_list_requires_hr_staff(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("accounts:users"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("accounts:users"))
        self.assertEqual(response.status_code, 200)

    def test_organization_departments_requires_hr_staff(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("organization:departments"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("organization:departments"))
        self.assertEqual(response.status_code, 200)


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_command(self):
        from django.core.management import call_command

        call_command("seed_demo")
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertGreater(Employee.objects.count(), 0)
        self.assertGreater(LeaveRequest.objects.count(), 0)

    def test_seed_demo_is_idempotent(self):
        from django.core.management import call_command

        call_command("seed_demo")
        count_after_first = User.objects.count()
        call_command("seed_demo")
        self.assertEqual(User.objects.count(), count_after_first)
