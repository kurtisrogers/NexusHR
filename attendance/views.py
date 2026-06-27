from datetime import date, datetime, time

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import ListView

from accounts.mixins import HRStaffRequiredMixin
from attendance.models import AttendanceRecord, AttendanceStatus


class AttendanceListView(LoginRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = "attendance/attendance_list.html"
    context_object_name = "records"
    paginate_by = 31

    def get_queryset(self):
        qs = AttendanceRecord.objects.select_related("employee__user")
        user = self.request.user
        if user.is_hr_staff:
            return qs
        if hasattr(user, "employee_profile"):
            return qs.filter(employee=user.employee_profile)
        return qs.none()


def clock_in(request):
    if not hasattr(request.user, "employee_profile"):
        messages.error(request, "No employee profile found.")
        return redirect("reports:dashboard")
    employee = request.user.employee_profile
    today = timezone.localdate()
    now = timezone.localtime().time()
    record, created = AttendanceRecord.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={"clock_in": now, "status": AttendanceStatus.PRESENT},
    )
    if not created and not record.clock_in:
        record.clock_in = now
        record.status = AttendanceStatus.PRESENT
        record.save()
        messages.success(request, f"Clocked in at {now.strftime('%H:%M')}.")
    elif created:
        messages.success(request, f"Clocked in at {now.strftime('%H:%M')}.")
    else:
        messages.info(request, "Already clocked in today.")
    if request.htmx:
        return render(request, "attendance/partials/clock_status.html", {"record": record})
    return redirect("attendance:list")


def clock_out(request):
    if not hasattr(request.user, "employee_profile"):
        return redirect("reports:dashboard")
    employee = request.user.employee_profile
    today = timezone.localdate()
    now = timezone.localtime().time()
    try:
        record = AttendanceRecord.objects.get(employee=employee, date=today)
        record.clock_out = now
        if record.clock_in:
            cin = datetime.combine(today, record.clock_in)
            cout = datetime.combine(today, now)
            delta = cout - cin
            record.hours_worked = round(delta.total_seconds() / 3600, 2)
        record.save()
        messages.success(request, f"Clocked out at {now.strftime('%H:%M')}.")
    except AttendanceRecord.DoesNotExist:
        messages.error(request, "No clock-in record for today.")
        record = None
    if request.htmx:
        return render(request, "attendance/partials/clock_status.html", {"record": record})
    return redirect("attendance:list")
