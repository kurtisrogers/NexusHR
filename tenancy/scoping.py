from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q, QuerySet

if TYPE_CHECKING:
    from organization.models import Company


class TenantScope:
    """Centralized tenant-scoped queryset helpers."""

    def __init__(self, company: Company):
        self.company = company

    def users(self):
        from accounts.models import User

        return User.objects.filter(company=self.company)

    def employees(self):
        from employees.models import Employee

        return Employee.objects.filter(company=self.company)

    def departments(self):
        from organization.models import Department

        return Department.objects.filter(company=self.company)

    def locations(self):
        from organization.models import Location

        return Location.objects.filter(company=self.company)

    def job_titles(self):
        from organization.models import JobTitle

        return JobTitle.objects.filter(department__company=self.company)

    def leave_types(self):
        from leave.models import LeaveType

        return LeaveType.objects.filter(company=self.company)

    def leave_requests(self):
        from leave.models import LeaveRequest

        return LeaveRequest.objects.filter(employee__company=self.company)

    def leave_balances(self):
        from leave.models import LeaveBalance

        return LeaveBalance.objects.filter(employee__company=self.company)

    def attendance_records(self):
        from attendance.models import AttendanceRecord

        return AttendanceRecord.objects.filter(employee__company=self.company)

    def job_postings(self):
        from recruitment.models import JobPosting

        return JobPosting.objects.filter(department__company=self.company)

    def applicants(self):
        from recruitment.models import Applicant

        return Applicant.objects.filter(company=self.company)

    def applications(self):
        from recruitment.models import Application

        return Application.objects.filter(job__department__company=self.company)

    def review_cycles(self):
        from performance.models import ReviewCycle

        return ReviewCycle.objects.filter(company=self.company)

    def goals(self):
        from performance.models import Goal

        return Goal.objects.filter(employee__company=self.company)

    def performance_reviews(self):
        from performance.models import PerformanceReview

        return PerformanceReview.objects.filter(employee__company=self.company)

    def payslips(self):
        from payroll.models import Payslip

        return Payslip.objects.filter(employee__company=self.company)

    def salary_structures(self):
        from payroll.models import SalaryStructure

        return SalaryStructure.objects.filter(employee__company=self.company)

    def expense_categories(self):
        from expenses.models import ExpenseCategory

        return ExpenseCategory.objects.filter(company=self.company)

    def expense_claims(self):
        from expenses.models import ExpenseClaim

        return ExpenseClaim.objects.filter(employee__company=self.company)

    def announcements(self):
        from announcements.models import Announcement

        return Announcement.objects.filter(author__company=self.company)

    def policy_documents(self):
        from announcements.models import PolicyDocument

        return PolicyDocument.objects.filter(company=self.company)

    def employee_detail_queryset(self):
        return self.employees().select_related(
            "user", "department", "job_title", "location", "manager__user"
        )

    def filter_employee_visibility(self, qs: QuerySet, user) -> QuerySet:
        if user.is_hr_staff:
            return qs
        if user.is_manager_or_above and hasattr(user, "employee_profile"):
            profile = user.employee_profile
            return qs.filter(Q(manager=profile) | Q(pk=profile.pk))
        if hasattr(user, "employee_profile"):
            return qs.filter(pk=user.employee_profile.pk)
        return qs.none()

    def filter_leave_requests(self, qs: QuerySet, user) -> QuerySet:
        if user.is_hr_staff:
            return qs
        if user.is_manager_or_above and hasattr(user, "employee_profile"):
            profile = user.employee_profile
            return qs.filter(Q(employee__manager=profile) | Q(employee=profile))
        if hasattr(user, "employee_profile"):
            return qs.filter(employee=user.employee_profile)
        return qs.none()

    def filter_expense_claims(self, qs: QuerySet, user) -> QuerySet:
        return self.filter_leave_requests(qs, user)

    def filter_goals(self, qs: QuerySet, user) -> QuerySet:
        if user.is_hr_staff:
            return qs
        if hasattr(user, "employee_profile"):
            profile = user.employee_profile
            if user.is_manager_or_above:
                return qs.filter(Q(employee=profile) | Q(employee__manager=profile))
            return qs.filter(employee=profile)
        return qs.none()

    def filter_reviews(self, qs: QuerySet, user) -> QuerySet:
        if user.is_hr_staff:
            return qs
        if hasattr(user, "employee_profile"):
            profile = user.employee_profile
            return qs.filter(Q(employee=profile) | Q(reviewer=user))
        return qs.none()

    def filter_announcements(self, qs: QuerySet, user) -> QuerySet:
        if user.is_hr_staff:
            return qs
        if hasattr(user, "employee_profile") and user.employee_profile.department:
            dept = user.employee_profile.department
            return qs.filter(Q(department__isnull=True) | Q(department=dept))
        return qs.filter(department__isnull=True)

    def object_in_tenant(self, obj) -> bool:
        company_id = self.company.id
        if hasattr(obj, "company_id") and obj.company_id:
            return obj.company_id == company_id
        if hasattr(obj, "user") and getattr(obj.user, "company_id", None):
            return obj.user.company_id == company_id
        if hasattr(obj, "employee") and getattr(obj.employee, "company_id", None):
            return obj.employee.company_id == company_id
        if hasattr(obj, "department") and obj.department and obj.department.company_id:
            return obj.department.company_id == company_id
        if hasattr(obj, "author") and getattr(obj.author, "company_id", None):
            return obj.author.company_id == company_id
        if hasattr(obj, "job") and obj.job.department and obj.job.department.company_id:
            return obj.job.department.company_id == company_id
        return False


def get_scope(request) -> TenantScope:
    return TenantScope(request.tenant)
