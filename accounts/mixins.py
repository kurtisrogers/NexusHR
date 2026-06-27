from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import UserRole


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: set[str] = set()

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class HRStaffRequiredMixin(RoleRequiredMixin):
    allowed_roles = {
        UserRole.SUPER_ADMIN,
        UserRole.HR_ADMIN,
        UserRole.HR_MANAGER,
    }


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = {
        UserRole.SUPER_ADMIN,
        UserRole.HR_ADMIN,
        UserRole.HR_MANAGER,
        UserRole.MANAGER,
    }


class RecruiterRequiredMixin(RoleRequiredMixin):
    allowed_roles = {
        UserRole.SUPER_ADMIN,
        UserRole.HR_ADMIN,
        UserRole.HR_MANAGER,
        UserRole.RECRUITER,
    }


class SuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = {UserRole.SUPER_ADMIN}
