from django.db import models


class Plan(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    price_monthly_cents = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(
        default=25,
        help_text="0 = unlimited",
    )
    features = models.JSONField(default=list)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "price_monthly_cents"]

    def __str__(self):
        return self.name

    @property
    def price_display(self) -> str:
        if self.price_monthly_cents == 0:
            return "Custom"
        return f"${self.price_monthly_cents / 100:,.0f}"

    @property
    def employee_limit_display(self) -> str:
        if self.max_employees == 0:
            return "Unlimited"
        return str(self.max_employees)


class SubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", "Trialing"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past Due"
    CANCELED = "canceled", "Canceled"
    INCOMPLETE = "incomplete", "Incomplete"


class Subscription(models.Model):
    company = models.OneToOneField(
        "organization.Company",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING,
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name} — {self.plan.name} ({self.status})"

    @property
    def is_active(self) -> bool:
        return self.status in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        }
