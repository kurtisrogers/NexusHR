from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from employees.models import Employee
from hrms.test_utils import create_company, create_tenant_subscription, create_user
from leave.models import LeaveRequest

TENANT_HOST = "testco.localhost"


def tenant_host(subdomain: str) -> str:
    return f"{subdomain}.localhost"


class NexusHRTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = create_company(name="Demo Co", subdomain="testco")
        create_tenant_subscription(self.company)
        self.user = create_user("testuser", company=self.company)

    def test_landing_page_loads(self):
        response = self.client.get(reverse("marketing:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NexusHR")

    def test_login_page_loads_on_tenant(self):
        response = self.client.get(reverse("accounts:login"), HTTP_HOST=TENANT_HOST)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_auth(self):
        response = self.client.get(reverse("reports:dashboard"), HTTP_HOST=TENANT_HOST)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_dashboard(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"), HTTP_HOST=TENANT_HOST)
        self.assertEqual(response.status_code, 200)

    def test_seed_demo_command(self):
        User.objects.filter(username="admin").delete()
        call_command("seed_plans")
        call_command("seed_demo")
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertGreater(Employee.objects.count(), 0)
        self.assertGreater(LeaveRequest.objects.count(), 0)


class UserModelTests(TestCase):
    def setUp(self):
        self.company = create_company()

    def test_display_name_uses_full_name(self):
        user = create_user("jdoe", first_name="Jane", last_name="Doe", company=self.company)
        self.assertEqual(user.display_name, "Jane Doe")

    def test_display_name_falls_back_to_username(self):
        user = create_user("jdoe", first_name="", last_name="", company=self.company)
        self.assertEqual(user.display_name, "jdoe")

    def test_role_properties(self):
        hr_admin = create_user("hr", role=UserRole.HR_ADMIN, company=self.company)
        manager = create_user("mgr", role=UserRole.MANAGER, company=self.company)
        recruiter = create_user("rec", role=UserRole.RECRUITER, company=self.company)
        employee = create_user("emp", role=UserRole.EMPLOYEE, company=self.company)

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
        self.company = create_company(subdomain="demo")
        create_tenant_subscription(self.company)
        self.employee = create_user("employee", company=self.company)
        self.hr_admin = create_user("hr.admin", role=UserRole.HR_ADMIN, company=self.company)

    def test_employee_cannot_access_user_list(self):
        self.client.login(username="employee", password="testpass123")
        response = self.client.get(
            reverse("accounts:users"),
            HTTP_HOST=tenant_host(self.company.subdomain),
        )
        self.assertEqual(response.status_code, 403)

    def test_hr_admin_can_access_user_list(self):
        self.client.login(username="hr.admin", password="testpass123")
        response = self.client.get(
            reverse("accounts:users"),
            HTTP_HOST=tenant_host(self.company.subdomain),
        )
        self.assertEqual(response.status_code, 200)


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.client = Client()
        call_command("seed_plans")
        self.company_a = create_company(name="Company A", subdomain="acme")
        self.company_b = create_company(name="Company B", subdomain="beta")
        create_tenant_subscription(self.company_a)
        create_tenant_subscription(self.company_b)
        self.user_a = create_user("user_a", company=self.company_a)
        self.user_b = create_user("user_b", company=self.company_b)

    def test_user_cannot_login_on_wrong_tenant(self):
        self.client.login(username="user_a", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"), HTTP_HOST="beta.localhost")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
