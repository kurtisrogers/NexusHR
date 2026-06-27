from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import User
from announcements.models import Announcement
from attendance.models import AttendanceRecord
from employees.models import Employee, EmploymentStatus
from expenses.models import ExpenseClaim, ExpenseStatus
from leave.models import LeaveRequest, LeaveRequestStatus
from recruitment.models import Application, JobPosting


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        ctx["total_employees"] = Employee.objects.filter(
            status=EmploymentStatus.ACTIVE
        ).count()
        ctx["pending_leaves"] = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.PENDING
        ).count()
        ctx["open_jobs"] = JobPosting.objects.filter(status="open").count()
        ctx["pending_expenses"] = ExpenseClaim.objects.filter(
            status=ExpenseStatus.SUBMITTED
        ).count()
        ctx["recent_announcements"] = Announcement.objects.filter(is_active=True)[:5]
        ctx["today_attendance"] = AttendanceRecord.objects.filter(date=today).count()

        if hasattr(user, "employee_profile"):
            emp = user.employee_profile
            ctx["my_leaves"] = LeaveRequest.objects.filter(employee=emp)[:5]
            ctx["my_attendance"] = AttendanceRecord.objects.filter(employee=emp)[:7]
            try:
                ctx["today_record"] = AttendanceRecord.objects.get(
                    employee=emp, date=today
                )
            except AttendanceRecord.DoesNotExist:
                ctx["today_record"] = None

        if user.is_manager_or_above and hasattr(user, "employee_profile"):
            mgr = user.employee_profile
            ctx["team_size"] = Employee.objects.filter(
                manager=mgr, status=EmploymentStatus.ACTIVE
            ).count()
            ctx["team_pending_leaves"] = LeaveRequest.objects.filter(
                employee__manager=mgr,
                status=LeaveRequestStatus.PENDING,
            ).count()

        dept_stats = (
            Employee.objects.filter(status=EmploymentStatus.ACTIVE)
            .values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:6]
        )
        ctx["department_stats"] = dept_stats
        return ctx
