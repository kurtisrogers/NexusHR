from decimal import Decimal

from django.conf import settings
from django.db import models


class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    default_days = models.PositiveSmallIntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default="#3b82f6")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    allocated = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    carried_over = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ["employee", "leave_type", "year"]
        ordering = ["-year", "leave_type__name"]

    @property
    def remaining(self):
        return self.allocated + self.carried_over - self.used

    def __str__(self):
        return f"{self.employee} — {self.leave_type} ({self.year})"


class LeaveRequestStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending Approval"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=LeaveRequestStatus.choices,
        default=LeaveRequestStatus.PENDING,
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )
    approver_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} — {self.leave_type} ({self.start_date})"

    def approve(self, approver, notes=""):
        self.status = LeaveRequestStatus.APPROVED
        self.approver = approver
        self.approver_notes = notes
        self.save()
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=self.employee,
            leave_type=self.leave_type,
            year=self.start_date.year,
            defaults={"allocated": self.leave_type.default_days},
        )
        balance.used = Decimal(str(balance.used)) + Decimal(str(self.days))
        balance.save(update_fields=["used"])

    def reject(self, approver, notes=""):
        self.status = LeaveRequestStatus.REJECTED
        self.approver = approver
        self.approver_notes = notes
        self.save()
