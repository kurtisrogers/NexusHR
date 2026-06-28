from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, ListView

from billing.entitlements import Feature
from leave.forms import LeaveApprovalForm, LeaveRequestForm
from leave.models import LeaveBalance, LeaveRequest, LeaveRequestStatus
from tenancy.mixins import FeatureRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class LeaveRequestListView(TenantUserRequiredMixin, ListView):
    model = LeaveRequest
    template_name = "leave/leave_list.html"
    context_object_name = "requests"
    paginate_by = 20

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.leave_requests().select_related("employee__user", "leave_type", "approver")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return scope.filter_leave_requests(qs, self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        scope = get_scope(self.request)
        ctx["status_filter"] = self.request.GET.get("status", "")
        ctx["pending_count"] = scope.leave_requests().filter(
            status=LeaveRequestStatus.PENDING
        ).count()
        return ctx


class LeaveRequestCreateView(FeatureRequiredMixin, TenantUserRequiredMixin, CreateView):
    required_feature = Feature.LEAVE
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = "leave/leave_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        employee = self.request.user.employee_profile
        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]
        days = (end - start).days + 1
        form.instance.employee = employee
        form.instance.days = max(days, 1)
        form.instance.status = LeaveRequestStatus.PENDING
        messages.success(self.request, "Leave request submitted.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("leave:list")


def leave_balances(request):
    if not request.user.is_authenticated or not request.tenant:
        return redirect("accounts:login")
    if not hasattr(request.user, "employee_profile"):
        return redirect("reports:dashboard")
    employee = request.user.employee_profile
    year = timezone.now().year
    balances = LeaveBalance.objects.filter(employee=employee, year=year).select_related(
        "leave_type"
    )
    return render(
        request,
        "leave/balances.html",
        {"balances": balances, "year": year},
    )


def approve_leave(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    scope = get_scope(request)
    leave = get_object_or_404(scope.leave_requests(), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        form = LeaveApprovalForm(request.POST)
        notes = form.cleaned_data["notes"] if form.is_valid() else ""
        if action == "approve":
            leave.approve(request.user, notes)
            messages.success(request, "Leave approved.")
        elif action == "reject":
            leave.reject(request.user, notes)
            messages.success(request, "Leave rejected.")
        if request.htmx:
            return render(
                request,
                "leave/partials/request_row.html",
                {"req": leave},
            )
        return redirect("leave:list")
    return render(
        request,
        "leave/partials/approval_form.html",
        {"leave": leave, "form": LeaveApprovalForm()},
    )
