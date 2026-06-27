from datetime import date
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from hrms.test_utils import create_hr_setup
from payroll.models import PayFrequency, Payslip, PayslipStatus, SalaryStructure


class PayrollViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()
        SalaryStructure.objects.create(
            employee=self.data["employee"],
            base_salary=100000,
            pay_frequency=PayFrequency.MONTHLY,
            effective_date=date.today(),
        )
        Payslip.objects.create(
            employee=self.data["employee"],
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            base_salary=8333,
            allowances=500,
            deductions=100,
            tax=1800,
            net_pay=6933,
            status=PayslipStatus.PAID,
        )

    def test_employee_sees_own_payslips(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("payroll:payslips"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "6933")

    def test_hr_sees_salary_structures(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("payroll:salaries"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100000")

    def test_salary_gross_property(self):
        salary = SalaryStructure.objects.get(employee=self.data["employee"])
        self.assertEqual(salary.gross_salary, Decimal("100000"))
