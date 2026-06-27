from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import ListView

from accounts.forms import LoginForm
from accounts.mixins import HRStaffRequiredMixin
from accounts.models import User


class LoginPageView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutPageView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class UserListView(HRStaffRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
