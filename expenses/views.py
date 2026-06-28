from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, ListView

from billing.entitlements import Feature
from expenses.forms import ExpenseApprovalForm, ExpenseClaimForm
from expenses.models import ExpenseClaim, ExpenseStatus
from tenancy.mixins import FeatureRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class ExpenseListView(FeatureRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.EXPENSES
    model = ExpenseClaim
    template_name = "expenses/expense_list.html"
    context_object_name = "claims"
    paginate_by = 20

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.expense_claims().select_related("employee__user", "category", "approver")
        user = self.request.user
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return scope.filter_expense_claims(qs, user)


class ExpenseCreateView(FeatureRequiredMixin, TenantUserRequiredMixin, CreateView):
    required_feature = Feature.EXPENSES
    model = ExpenseClaim
    form_class = ExpenseClaimForm
    template_name = "expenses/expense_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        form.instance.status = ExpenseStatus.SUBMITTED
        messages.success(self.request, "Expense claim submitted.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("expenses:list")


def approve_expense(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    scope = get_scope(request)
    claim = get_object_or_404(scope.expense_claims(), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        form = ExpenseApprovalForm(request.POST)
        notes = form.cleaned_data["notes"] if form.is_valid() else ""
        if action == "approve":
            claim.status = ExpenseStatus.APPROVED
            claim.approver = request.user
            claim.approver_notes = notes
            claim.save()
            messages.success(request, "Expense approved.")
        elif action == "reject":
            claim.status = ExpenseStatus.REJECTED
            claim.approver = request.user
            claim.approver_notes = notes
            claim.save()
            messages.success(request, "Expense rejected.")
        if request.htmx:
            return render(
                request,
                "expenses/partials/claim_row.html",
                {"claim": claim},
            )
        return redirect("expenses:list")
    return render(
        request,
        "expenses/partials/approval_form.html",
        {"claim": claim, "form": ExpenseApprovalForm()},
    )
