from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from django.views.generic import ListView

from accounts.forms import LoginForm
from accounts.mixins import HRStaffRequiredMixin
from accounts.models import User
from tenancy.mixins import TenantRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class LoginPageView(TenantRequiredMixin, LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class LogoutPageView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class UserListView(HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return get_scope(self.request).users()


class TenantPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/emails/password_reset.txt"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class TenantPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class TenantPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class TenantPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
