from django import forms

from announcements.models import Announcement, PolicyDocument


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "content",
            "priority",
            "department",
            "is_pinned",
            "expires_at",
            "is_active",
        ]
        widgets = {"expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class PolicyDocumentForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title", "category", "content", "version", "file", "effective_date", "is_active"]
        widgets = {"effective_date": forms.DateInput(attrs={"type": "date"})}
