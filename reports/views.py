from django.db.models import Count
from django.utils import timezone
from django.views.generic import TemplateView

from attendance.models import AttendanceRecord
from employees.models import EmploymentStatus
from expenses.models import ExpenseStatus
from leave.models import LeaveRequestStatus
from tenancy.mixins import TenantUserRequiredMixin
from tenancy.scoping import get_scope


class DashboardView(TenantUserRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        scope = get_scope(self.request)

        ctx["total_employees"] = scope.employees().filter(status=EmploymentStatus.ACTIVE).count()
        ctx["pending_leaves"] = (
            scope.leave_requests().filter(status=LeaveRequestStatus.PENDING).count()
        )
        ctx["open_jobs"] = scope.job_postings().filter(status="open").count()
        ctx["pending_expenses"] = (
            scope.expense_claims().filter(status=ExpenseStatus.SUBMITTED).count()
        )
        ctx["recent_announcements"] = scope.announcements().filter(is_active=True)[:5]
        ctx["today_attendance"] = scope.attendance_records().filter(date=today).count()

        if hasattr(user, "employee_profile"):
            emp = user.employee_profile
            ctx["my_leaves"] = scope.leave_requests().filter(employee=emp)[:5]
            ctx["my_attendance"] = scope.attendance_records().filter(employee=emp)[:7]
            try:
                ctx["today_record"] = AttendanceRecord.objects.get(employee=emp, date=today)
            except AttendanceRecord.DoesNotExist:
                ctx["today_record"] = None

        if user.is_manager_or_above and hasattr(user, "employee_profile"):
            mgr = user.employee_profile
            ctx["team_size"] = (
                scope.employees().filter(manager=mgr, status=EmploymentStatus.ACTIVE).count()
            )
            ctx["team_pending_leaves"] = (
                scope.leave_requests()
                .filter(
                    employee__manager=mgr,
                    status=LeaveRequestStatus.PENDING,
                )
                .count()
            )

        dept_stats = (
            scope.employees()
            .filter(status=EmploymentStatus.ACTIVE)
            .values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:6]
        )
        ctx["department_stats"] = dept_stats
        return ctx
