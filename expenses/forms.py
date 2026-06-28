from django import forms

from expenses.models import ExpenseClaim
from tenancy.scoping import TenantScope


class ExpenseClaimForm(forms.ModelForm):
    class Meta:
        model = ExpenseClaim
        fields = [
            "category",
            "title",
            "amount",
            "currency",
            "expense_date",
            "description",
            "receipt",
        ]
        widgets = {"expense_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["category"].queryset = scope.expense_categories()


class ExpenseApprovalForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
