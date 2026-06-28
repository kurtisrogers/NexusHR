from django.conf import settings
from django.db import models


class ReviewCycleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"


class ReviewCycle(models.Model):
    company = models.ForeignKey(
        "organization.Company",
        on_delete=models.CASCADE,
        related_name="review_cycles",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=ReviewCycleStatus.choices,
        default=ReviewCycleStatus.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class GoalStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Goal(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="goals",
    )
    cycle = models.ForeignKey(
        ReviewCycle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goals",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=GoalStatus.choices,
        default=GoalStatus.NOT_STARTED,
    )
    weight = models.PositiveSmallIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ReviewStatus(models.TextChoices):
    SELF_REVIEW = "self_review", "Self Review Pending"
    MANAGER_REVIEW = "manager_review", "Manager Review Pending"
    COMPLETED = "completed", "Completed"


class PerformanceReview(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="performance_reviews",
    )
    cycle = models.ForeignKey(ReviewCycle, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="conducted_reviews",
    )
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.SELF_REVIEW,
    )
    self_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    self_comments = models.TextField(blank=True)
    manager_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    manager_comments = models.TextField(blank=True)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["employee", "cycle"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} — {self.cycle}"
