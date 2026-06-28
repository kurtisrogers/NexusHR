from django import forms

from announcements.models import Announcement, PolicyDocument
from tenancy.scoping import TenantScope


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

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["department"].queryset = scope.departments()


class PolicyDocumentForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title", "category", "content", "version", "file", "effective_date", "is_active"]
        widgets = {"effective_date": forms.DateInput(attrs={"type": "date"})}
