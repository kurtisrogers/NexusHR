from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from billing.views import StripeWebhookView

urlpatterns = [
    path("", include("marketing.urls")),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("app/", lambda r: redirect("reports:dashboard")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("organization/", include("organization.urls")),
    path("employees/", include("employees.urls")),
    path("leave/", include("leave.urls")),
    path("attendance/", include("attendance.urls")),
    path("recruitment/", include("recruitment.urls")),
    path("performance/", include("performance.urls")),
    path("payroll/", include("payroll.urls")),
    path("expenses/", include("expenses.urls")),
    path("announcements/", include("announcements.urls")),
    path("reports/", include("reports.urls")),
    path("billing/", include("billing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
