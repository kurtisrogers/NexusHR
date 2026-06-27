from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserRole
from employees.models import Employee
from hrms.test_utils import create_employee, create_hr_setup, create_user


class EmployeeListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_hr_sees_all_employees(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("employees:list"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["employees"]), 3)

    def test_employee_sees_only_self(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("employees:list"))
        self.assertEqual(response.status_code, 200)
        employees = list(response.context["employees"])
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0].employee_id, "EMP-001")

    def test_manager_sees_team_and_self(self):
        other_user = create_user("other", UserRole.EMPLOYEE)
        create_employee(other_user, "EMP-999", department=self.data["department"])
        self.client.login(username="mgr", password="testpass123")
        response = self.client.get(reverse("employees:list"))
        ids = {e.employee_id for e in response.context["employees"]}
        self.assertIn("EMP-001", ids)
        self.assertIn("EMP-MGR", ids)
        self.assertNotIn("EMP-999", ids)

    def test_search_filters_by_name(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("employees:list"), {"q": "emp"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context["employees"]), 0)


class EmployeeDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_employee_detail_loads(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(
            reverse("employees:detail", kwargs={"pk": self.data["employee"].pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EMP-001")


class EmployeeCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_hr_can_access_create_form(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("employees:create"))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_create(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("employees:create"))
        self.assertEqual(response.status_code, 403)

    def test_create_employee(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.post(
            reverse("employees:create"),
            {
                "username": "newhire",
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "Hire",
                "role": UserRole.EMPLOYEE,
                "employee_id": "EMP-NEW",
                "department": self.data["department"].pk,
                "employment_type": "full_time",
                "status": "active",
                "hire_date": date.today().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employee.objects.filter(employee_id="EMP-NEW").exists())
