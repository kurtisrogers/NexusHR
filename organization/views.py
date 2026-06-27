from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import HRStaffRequiredMixin
from organization.forms import CompanyForm, DepartmentForm, JobTitleForm, LocationForm
from organization.models import Company, Department, JobTitle, Location


class DepartmentListView(HRStaffRequiredMixin, ListView):
    model = Department
    template_name = "organization/department_list.html"
    context_object_name = "departments"


class DepartmentCreateView(HRStaffRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "organization/department_form.html"

    def form_valid(self, form):
        if not form.instance.company_id:
            form.instance.company = Company.objects.first()
        messages.success(self.request, "Department created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("organization:departments")


class LocationListView(HRStaffRequiredMixin, ListView):
    model = Location
    template_name = "organization/location_list.html"
    context_object_name = "locations"


class JobTitleListView(HRStaffRequiredMixin, ListView):
    model = JobTitle
    template_name = "organization/job_title_list.html"
    context_object_name = "job_titles"
