from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from accounts.mixins import SuperAdminRequiredMixin
from billing.entitlements import Feature, active_employee_count, employee_limit, get_plan
from billing.models import Plan
from billing.stripe_service import create_checkout_session, create_customer_portal_session, handle_webhook
from tenancy.mixins import TenantUserRequiredMixin
from tenancy.utils import tenant_absolute_url


class BillingSettingsView(TenantUserRequiredMixin, TemplateView):
    template_name = "billing/settings.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self.request.tenant
        plan = get_plan(company)
        ctx["subscription"] = getattr(company, "subscription", None)
        ctx["plan"] = plan
        ctx["plans"] = Plan.objects.filter(is_active=True)
        ctx["active_employees"] = active_employee_count(company)
        ctx["employee_limit"] = employee_limit(company)
        ctx["feature_labels"] = Feature.LABELS
        return ctx


class UpgradePlanView(SuperAdminRequiredMixin, TenantUserRequiredMixin, View):
    def post(self, request, slug):
        plan = Plan.objects.filter(slug=slug, is_active=True).first()
        if not plan:
            messages.error(request, "Plan not found.")
            return redirect("billing:settings")

        success_url = tenant_absolute_url(
            request.tenant.subdomain,
            reverse("billing:settings") + "?upgraded=1",
        )
        cancel_url = tenant_absolute_url(
            request.tenant.subdomain,
            reverse("billing:settings"),
        )
        checkout_url = create_checkout_session(
            request.tenant,
            plan,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(checkout_url)


class CustomerPortalView(SuperAdminRequiredMixin, TenantUserRequiredMixin, View):
    def post(self, request):
        return_url = tenant_absolute_url(
            request.tenant.subdomain,
            reverse("billing:settings"),
        )
        portal_url = create_customer_portal_session(request.tenant, return_url)
        return redirect(portal_url)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            handle_webhook(request.body, sig_header)
        except ValueError:
            return HttpResponseBadRequest("Invalid payload")
        except Exception as exc:
            if "SignatureVerificationError" in type(exc).__name__:
                return HttpResponseBadRequest("Invalid signature")
            raise
        return HttpResponse(status=200)
