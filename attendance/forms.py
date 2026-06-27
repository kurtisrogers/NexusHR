from django import forms

from attendance.models import AttendanceRecord


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ["date", "clock_in", "clock_out", "status", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "clock_in": forms.TimeInput(attrs={"type": "time"}),
            "clock_out": forms.TimeInput(attrs={"type": "time"}),
        }
