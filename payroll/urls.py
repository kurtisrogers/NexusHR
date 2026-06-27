from django.urls import path

from . import views

app_name = "payroll"

urlpatterns = [
    path("payslips/", views.PayslipListView.as_view(), name="payslips"),
    path("salaries/", views.SalaryListView.as_view(), name="salaries"),
]
