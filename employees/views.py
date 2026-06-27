from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import HRStaffRequiredMixin, ManagerRequiredMixin
from employees.forms import DocumentUploadForm, EmployeeForm, EmployeeProfileForm
from employees.models import Employee, EmployeeDocument


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 20

    def get_queryset(self):
        qs = Employee.objects.select_related(
            "user", "department", "job_title", "location", "manager__user"
        )
        user = self.request.user
        if user.is_hr_staff:
            return qs
        if user.is_manager_or_above and hasattr(user, "employee_profile"):
            return qs.filter(
                Q(manager=user.employee_profile) | Q(pk=user.employee_profile.pk)
            )
        if hasattr(user, "employee_profile"):
            return qs.filter(pk=user.employee_profile.pk)
        return qs.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search"] = self.request.GET.get("q", "")
        q = ctx["search"]
        if q:
            ctx["employees"] = self.get_queryset().filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(employee_id__icontains=q)
                | Q(user__email__icontains=q)
            )
        return ctx


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return Employee.objects.select_related(
            "user", "department", "job_title", "location", "manager__user"
        )


class EmployeeCreateView(HRStaffRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"

    def form_valid(self, form):
        from accounts.models import User

        data = form.cleaned_data
        user = User.objects.create_user(
            username=data.pop("username"),
            email=data.pop("email"),
            first_name=data.pop("first_name"),
            last_name=data.pop("last_name"),
            role=data.pop("role"),
            password="changeme123",
        )
        form.instance.user = user
        messages.success(self.request, f"Employee {user.display_name} created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("employees:detail", kwargs={"pk": self.object.pk})


class EmployeeProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeProfileForm
    template_name = "employees/profile_form.html"

    def get_object(self):
        if self.kwargs.get("pk"):
            return get_object_or_404(Employee, pk=self.kwargs["pk"])
        return self.request.user.employee_profile

    def get_success_url(self):
        return reverse("employees:profile")


def upload_document(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employee = employee
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, "Document uploaded.")
            if request.htmx:
                return render(
                    request,
                    "employees/partials/document_row.html",
                    {"doc": doc},
                )
            return redirect("employees:detail", pk=pk)
    else:
        form = DocumentUploadForm()
    return render(
        request,
        "employees/partials/document_form.html",
        {"form": form, "employee": employee},
    )
