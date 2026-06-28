from django.db import models


class WorkSchedule(models.Model):
    company = models.ForeignKey(
        "organization.Company",
        on_delete=models.CASCADE,
        related_name="work_schedules",
    )
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    work_days = models.CharField(
        max_length=20,
        default="1,2,3,4,5",
        help_text="Comma-separated weekday numbers (1=Mon, 7=Sun)",
    )
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    HALF_DAY = "half_day", "Half Day"
    REMOTE = "remote", "Remote"
    ON_LEAVE = "on_leave", "On Leave"


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ["employee", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} — {self.date}"
