from django import forms

from leave.models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class LeaveApprovalForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
