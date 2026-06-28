from django.views.generic import ListView

from accounts.mixins import HRStaffRequiredMixin
from billing.entitlements import Feature
from payroll.models import Payslip, SalaryStructure
from tenancy.mixins import FeatureRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class PayslipListView(FeatureRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.PAYROLL
    model = Payslip
    template_name = "payroll/payslip_list.html"
    context_object_name = "payslips"
    paginate_by = 12

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.payslips().select_related("employee__user")
        if self.request.user.is_hr_staff:
            return qs
        if hasattr(self.request.user, "employee_profile"):
            return qs.filter(employee=self.request.user.employee_profile)
        return qs.none()


class SalaryListView(FeatureRequiredMixin, HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.PAYROLL
    model = SalaryStructure
    template_name = "payroll/salary_list.html"
    context_object_name = "salaries"

    def get_queryset(self):
        return get_scope(self.request).salary_structures().select_related("employee__user")
