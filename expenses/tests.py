from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from expenses.models import ExpenseStatus
from hrms.test_utils import create_expense_claim, create_hr_setup


class ExpenseViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_employee_can_submit_expense(self):
        self.client.login(username="emp", password="testpass123")
        from hrms.test_utils import create_expense_category

        category = create_expense_category()
        response = self.client.post(
            reverse("expenses:create"),
            {
                "category": category.pk,
                "title": "Taxi fare",
                "amount": "45.00",
                "currency": "USD",
                "expense_date": date.today().isoformat(),
                "description": "Airport transfer",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.data["employee"].expense_claims.filter(status=ExpenseStatus.SUBMITTED).exists()
        )

    def test_manager_can_approve_expense(self):
        claim = create_expense_claim(self.data["employee"])
        self.client.login(username="mgr", password="testpass123")
        response = self.client.post(
            reverse("expenses:approve", kwargs={"pk": claim.pk}),
            {"action": "approve", "notes": "OK"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        claim.refresh_from_db()
        self.assertEqual(claim.status, ExpenseStatus.APPROVED)

    def test_employee_sees_own_claims_only(self):
        from accounts.models import UserRole
        from hrms.test_utils import create_employee, create_user

        create_expense_claim(self.data["employee"], title="Mine")
        other_user = create_user("other_emp", UserRole.EMPLOYEE)
        other_emp = create_employee(
            other_user,
            "EMP-OTHER",
            department=self.data["department"],
        )
        create_expense_claim(other_emp, title="Theirs")
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("expenses:list"))
        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Theirs")
