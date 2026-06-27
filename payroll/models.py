from django.db import models


class PayFrequency(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    BIWEEKLY = "biweekly", "Bi-weekly"
    WEEKLY = "weekly", "Weekly"


class SalaryStructure(models.Model):
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="salary",
    )
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    pay_frequency = models.CharField(
        max_length=20,
        choices=PayFrequency.choices,
        default=PayFrequency.MONTHLY,
    )
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    effective_date = models.DateField()

    @property
    def gross_salary(self):
        return (
            self.base_salary
            + self.housing_allowance
            + self.transport_allowance
            + self.other_allowances
        )

    def __str__(self):
        return f"{self.employee} — {self.base_salary} {self.currency}"


class PayslipStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PROCESSED = "processed", "Processed"
    PAID = "paid", "Paid"


class Payslip(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="payslips",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PayslipStatus.choices,
        default=PayslipStatus.DRAFT,
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_start"]
        unique_together = ["employee", "period_start", "period_end"]

    def __str__(self):
        return f"{self.employee} — {self.period_start} to {self.period_end}"
