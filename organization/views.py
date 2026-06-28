from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.generic import CreateView, ListView

from accounts.mixins import HRStaffRequiredMixin
from organization.forms import DepartmentForm
from organization.models import Department, JobTitle, Location
from tenancy.mixins import TenantUserRequiredMixin
from tenancy.scoping import get_scope


class DepartmentListView(HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    model = Department
    template_name = "organization/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return get_scope(self.request).departments()


class DepartmentCreateView(HRStaffRequiredMixin, TenantUserRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "organization/department_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.request.tenant
        messages.success(self.request, "Department created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("organization:departments")


class LocationListView(HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    model = Location
    template_name = "organization/location_list.html"
    context_object_name = "locations"

    def get_queryset(self):
        return get_scope(self.request).locations()


class JobTitleListView(HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    model = JobTitle
    template_name = "organization/job_title_list.html"
    context_object_name = "job_titles"

    def get_queryset(self):
        return get_scope(self.request).job_titles()
