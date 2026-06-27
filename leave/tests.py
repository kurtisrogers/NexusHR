from datetime import date
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from hrms.test_utils import (
    create_hr_setup,
    create_leave_request,
    create_leave_type,
)
from leave.models import LeaveBalance, LeaveRequestStatus


class LeaveBalanceModelTests(TestCase):
    def test_remaining_calculates_correctly(self):
        data = create_hr_setup()
        lt = create_leave_type(default_days=20)
        balance = LeaveBalance.objects.create(
            employee=data["employee"],
            leave_type=lt,
            year=date.today().year,
            allocated=20,
            used=5,
            carried_over=2,
        )
        self.assertEqual(balance.remaining, Decimal("17"))


class LeaveRequestModelTests(TestCase):
    def test_approve_updates_balance(self):
        data = create_hr_setup()
        lt = create_leave_type(default_days=20)
        req = create_leave_request(data["employee"], leave_type=lt)
        req.days = 3
        req.save()
        req.approve(data["manager_user"], notes="Approved")
        req.refresh_from_db()
        self.assertEqual(req.status, LeaveRequestStatus.APPROVED)
        balance = LeaveBalance.objects.get(
            employee=data["employee"],
            leave_type=lt,
            year=req.start_date.year,
        )
        self.assertEqual(balance.used, Decimal("3"))

    def test_reject_does_not_update_balance(self):
        data = create_hr_setup()
        lt = create_leave_type()
        req = create_leave_request(data["employee"], leave_type=lt)
        req.reject(data["manager_user"], notes="No")
        req.refresh_from_db()
        self.assertEqual(req.status, LeaveRequestStatus.REJECTED)
        self.assertFalse(
            LeaveBalance.objects.filter(employee=data["employee"], leave_type=lt).exists()
        )


class LeaveViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()
        self.leave_type = create_leave_type()

    def test_employee_can_submit_leave(self):
        self.client.login(username="emp", password="testpass123")
        from datetime import timedelta

        start = date.today() + timedelta(days=14)
        end = start + timedelta(days=2)
        response = self.client.post(
            reverse("leave:create"),
            {
                "leave_type": self.leave_type.pk,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "reason": "Vacation",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.data["employee"].leave_requests.filter(status=LeaveRequestStatus.PENDING).exists()
        )

    def test_manager_can_approve_leave_via_htmx(self):
        req = create_leave_request(self.data["employee"], leave_type=self.leave_type)
        self.client.login(username="mgr", password="testpass123")
        response = self.client.post(
            reverse("leave:approve", kwargs={"pk": req.pk}),
            {"action": "approve", "notes": "Enjoy"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, LeaveRequestStatus.APPROVED)

    def test_leave_balances_page(self):
        LeaveBalance.objects.create(
            employee=self.data["employee"],
            leave_type=self.leave_type,
            year=date.today().year,
            allocated=20,
        )
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("leave:balances"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annual Leave")
