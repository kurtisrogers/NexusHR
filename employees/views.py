from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import HRStaffRequiredMixin
from billing.entitlements import can_add_employee
from employees.forms import DocumentUploadForm, EmployeeForm, EmployeeProfileForm
from employees.models import Employee
from tenancy.mixins import TenantUserRequiredMixin
from tenancy.scoping import get_scope


class EmployeeListView(TenantUserRequiredMixin, ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 20

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.employee_detail_queryset()
        return scope.filter_employee_visibility(qs, self.request.user)

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


class EmployeeDetailView(TenantUserRequiredMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        scope = get_scope(self.request)
        return scope.filter_employee_visibility(scope.employee_detail_queryset(), self.request.user)


class EmployeeCreateView(HRStaffRequiredMixin, TenantUserRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not can_add_employee(request.tenant):
            messages.error(
                request,
                "Employee limit reached for your plan. Upgrade to add more employees.",
            )
            return redirect("billing:settings")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        from accounts.models import User

        data = form.cleaned_data
        user = User.objects.create_user(
            username=data.pop("username"),
            email=data.pop("email"),
            first_name=data.pop("first_name"),
            last_name=data.pop("last_name"),
            role=data.pop("role"),
            company=self.request.tenant,
            password="changeme123",
        )
        form.instance.user = user
        form.instance.company = self.request.tenant
        messages.success(self.request, f"Employee {user.display_name} created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("employees:detail", kwargs={"pk": self.object.pk})


class EmployeeProfileUpdateView(TenantUserRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeProfileForm
    template_name = "employees/profile_form.html"

    def get_object(self):
        scope = get_scope(self.request)
        if self.kwargs.get("pk"):
            return get_object_or_404(
                scope.filter_employee_visibility(scope.employee_detail_queryset(), self.request.user),
                pk=self.kwargs["pk"],
            )
        return self.request.user.employee_profile

    def get_success_url(self):
        return reverse("employees:profile")


def upload_document(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    scope = get_scope(request)
    employee = get_object_or_404(
        scope.filter_employee_visibility(scope.employee_detail_queryset(), request.user),
        pk=pk,
    )
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
