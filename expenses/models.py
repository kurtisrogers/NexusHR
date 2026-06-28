from django.conf import settings
from django.db import models


class ExpenseCategory(models.Model):
    company = models.ForeignKey(
        "organization.Company",
        on_delete=models.CASCADE,
        related_name="expense_categories",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requires_receipt = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "expense categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_expense_category_code_per_company",
            ),
        ]

    def __str__(self):
        return self.name


class ExpenseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    REIMBURSED = "reimbursed", "Reimbursed"


class ExpenseClaim(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="expense_claims",
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    expense_date = models.DateField()
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="expense_receipts/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ExpenseStatus.choices,
        default=ExpenseStatus.DRAFT,
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses",
    )
    approver_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.amount} {self.currency}"
