from django import forms

from organization.models import Company, Department, JobTitle, Location
from tenancy.scoping import TenantScope


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "manager", "parent", "is_active"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["manager"].queryset = scope.users()
            self.fields["parent"].queryset = scope.departments()


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "address", "city", "country", "is_headquarters"]


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = ["title", "department", "level", "description", "min_salary", "max_salary"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["department"].queryset = scope.departments()
