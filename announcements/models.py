from django.conf import settings
from django.db import models

from organization.models import Department


class AnnouncementPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    priority = models.CharField(
        max_length=10,
        choices=AnnouncementPriority.choices,
        default=AnnouncementPriority.NORMAL,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Leave blank for company-wide announcement",
    )
    is_pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_pinned", "-published_at"]

    def __str__(self):
        return self.title


class PolicyDocument(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default="General")
    content = models.TextField()
    version = models.CharField(max_length=20, default="1.0")
    file = models.FileField(upload_to="policies/", blank=True, null=True)
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return f"{self.title} v{self.version}"
