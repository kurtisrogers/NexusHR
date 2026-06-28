from django import forms

from leave.models import LeaveRequest
from tenancy.scoping import TenantScope


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["leave_type"].queryset = scope.leave_types()


class LeaveApprovalForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
