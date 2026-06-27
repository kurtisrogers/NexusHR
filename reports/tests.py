from django.test import Client, TestCase
from django.urls import reverse

from employees.models import EmploymentStatus
from expenses.models import ExpenseStatus
from hrms.test_utils import create_expense_claim, create_hr_setup, create_leave_request
from leave.models import LeaveRequestStatus


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_dashboard_shows_kpis(self):
        create_leave_request(
            self.data["employee"],
            status=LeaveRequestStatus.PENDING,
        )
        create_expense_claim(self.data["employee"], status=ExpenseStatus.SUBMITTED)
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Employees")
        self.assertGreaterEqual(response.context["total_employees"], 1)
        self.assertGreaterEqual(response.context["pending_leaves"], 1)
        self.assertGreaterEqual(response.context["pending_expenses"], 1)

    def test_manager_sees_team_stats(self):
        self.client.login(username="mgr", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("team_size", response.context)
        self.assertGreaterEqual(response.context["team_size"], 1)

    def test_employee_sees_clock_widget_context(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("my_leaves", response.context)

    def test_active_employee_count_excludes_terminated(self):
        self.data["employee"].status = EmploymentStatus.TERMINATED
        self.data["employee"].save()
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("reports:dashboard"))
        active = response.context["total_employees"]
        self.assertEqual(
            active,
            self.data["employee"]
            .__class__.objects.filter(
                status=EmploymentStatus.ACTIVE,
            )
            .count(),
        )
