from django import forms

from expenses.models import ExpenseClaim


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


class ExpenseApprovalForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
