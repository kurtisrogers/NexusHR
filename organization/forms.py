from django import forms

from organization.models import Company, Department, JobTitle, Location


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "manager", "parent", "is_active"]


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "address", "city", "country", "is_headquarters"]


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = ["title", "department", "level", "description", "min_salary", "max_salary"]
