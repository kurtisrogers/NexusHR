from django.test import TestCase

from hrms.test_utils import create_company, create_department, create_employee, create_user


class EmployeeModelTests(TestCase):
    def test_str_representation(self):
        company = create_company()
        department = create_department(company, name="People Ops")
        user = create_user("employee", first_name="Alex", last_name="Rivera")
        employee = create_employee(user, employee_id="EMP-100", department=department)

        self.assertEqual(str(employee), "EMP-100 — Alex Rivera")
