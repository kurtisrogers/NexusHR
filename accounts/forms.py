from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "autofocus": True})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(request, *args, **kwargs)

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        tenant = getattr(self.request, "tenant", None)
        if tenant and user.company_id != tenant.id:
            raise ValidationError(
                "Invalid credentials for this organization.",
                code="invalid_login",
            )


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "phone", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
