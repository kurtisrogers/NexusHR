from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import User
from billing.models import Plan
from organization.models import Company
from tenancy.utils import RESERVED_SUBDOMAINS, validate_subdomain


class SignupForm(forms.Form):
    company_name = forms.CharField(max_length=200, label="Company name")
    subdomain = forms.SlugField(
        max_length=63,
        label="Workspace subdomain",
        help_text="Your team will sign in at yourname.localhost",
    )
    admin_first_name = forms.CharField(max_length=150)
    admin_last_name = forms.CharField(max_length=150)
    admin_email = forms.EmailField()
    admin_username = forms.CharField(max_length=150)
    admin_password = forms.CharField(widget=forms.PasswordInput())
    plan = forms.ModelChoiceField(queryset=Plan.objects.filter(is_active=True), empty_label=None)

    def clean_subdomain(self):
        subdomain = self.cleaned_data["subdomain"].lower()
        error = validate_subdomain(subdomain)
        if error:
            raise ValidationError(error)
        if Company.objects.filter(subdomain=subdomain).exists():
            raise ValidationError("This subdomain is already taken.")
        return subdomain

    def clean_admin_username(self):
        username = self.cleaned_data["admin_username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_admin_email(self):
        email = self.cleaned_data["admin_email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_admin_password(self):
        password = self.cleaned_data["admin_password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        subdomain = cleaned.get("subdomain")
        if subdomain and subdomain in RESERVED_SUBDOMAINS:
            self.add_error("subdomain", "This subdomain is reserved.")
        return cleaned
