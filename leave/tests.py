from datetime import date
from decimal import Decimal

from django.test import TestCase

from accounts.models import UserRole
from hrms.test_utils import (
    create_company,
    create_department,
    create_employee,
    create_leave_balance,
    create_leave_type,
    create_user,
)
from leave.models import LeaveRequest, LeaveRequestStatus


class LeaveBalanceTests(TestCase):
    def setUp(self):
        company = create_company()
        department = create_department(company)
        user = create_user("leave-user")
        self.employee = create_employee(user, employee_id="EMP-001", department=department)
        self.leave_type = create_leave_type()

    def test_remaining_balance(self):
        balance = create_leave_balance(
            self.employee,
            self.leave_type,
            allocated=Decimal("20"),
            used=Decimal("5"),
            carried_over=Decimal("2"),
        )
        self.assertEqual(balance.remaining, Decimal("17"))


class LeaveRequestWorkflowTests(TestCase):
    def setUp(self):
        company = create_company()
        department = create_department(company)
        self.employee_user = create_user("employee")
        self.manager_user = create_user("manager", role=UserRole.MANAGER)
        self.employee = create_employee(
            self.employee_user,
            employee_id="EMP-002",
            department=department,
        )
        self.leave_type = create_leave_type(default_days=10)

    def test_approve_updates_balance(self):
        request = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            start_date=date(2024, 6, 3),
            end_date=date(2024, 6, 5),
            days=Decimal("3"),
            status=LeaveRequestStatus.PENDING,
        )

        request.approve(self.manager_user, notes="Approved")

        request.refresh_from_db()
        self.assertEqual(request.status, LeaveRequestStatus.APPROVED)
        self.assertEqual(request.approver, self.manager_user)
        self.assertEqual(request.approver_notes, "Approved")

        balance = self.employee.leave_balances.get(
            leave_type=self.leave_type,
            year=2024,
        )
        self.assertEqual(balance.used, Decimal("3"))
        self.assertEqual(balance.allocated, Decimal("10"))

    def test_reject_does_not_update_balance(self):
        request = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 2),
            days=Decimal("2"),
            status=LeaveRequestStatus.PENDING,
        )

        request.reject(self.manager_user, notes="Not enough coverage")

        request.refresh_from_db()
        self.assertEqual(request.status, LeaveRequestStatus.REJECTED)
        self.assertFalse(self.employee.leave_balances.exists())
