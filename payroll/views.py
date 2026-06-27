from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from accounts.mixins import HRStaffRequiredMixin
from payroll.models import Payslip, SalaryStructure


class PayslipListView(LoginRequiredMixin, ListView):
    model = Payslip
    template_name = "payroll/payslip_list.html"
    context_object_name = "payslips"
    paginate_by = 12

    def get_queryset(self):
        qs = Payslip.objects.select_related("employee__user")
        if self.request.user.is_hr_staff:
            return qs
        if hasattr(self.request.user, "employee_profile"):
            return qs.filter(employee=self.request.user.employee_profile)
        return qs.none()


class SalaryListView(HRStaffRequiredMixin, ListView):
    model = SalaryStructure
    template_name = "payroll/salary_list.html"
    context_object_name = "salaries"

    def get_queryset(self):
        return SalaryStructure.objects.select_related("employee__user")
