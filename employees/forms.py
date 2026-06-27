from django import forms

from accounts.models import UserRole
from employees.models import Employee, EmployeeDocument


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    role = forms.ChoiceField(choices=UserRole.choices)

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "department",
            "job_title",
            "location",
            "manager",
            "employment_type",
            "status",
            "hire_date",
            "date_of_birth",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bio",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields["username"].initial = user.username
            self.fields["email"].initial = user.email
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["role"].initial = user.role


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bio",
        ]


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ["title", "document_type", "file"]
