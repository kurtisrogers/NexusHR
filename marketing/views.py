from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from accounts.models import User, UserRole
from billing.models import SubscriptionStatus
from billing.stripe_service import (
    create_checkout_session,
    create_trial_subscription,
    stripe_enabled,
)
from marketing.forms import SignupForm
from organization.models import Company
from tenancy.utils import public_absolute_url, tenant_absolute_url


class PublicSiteMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.is_public_site:
            return redirect(tenant_absolute_url(request.tenant.subdomain, "/"))
        return super().dispatch(request, *args, **kwargs)


class LandingView(PublicSiteMixin, TemplateView):
    template_name = "marketing/landing.html"


class PricingView(PublicSiteMixin, TemplateView):
    template_name = "marketing/pricing.html"

    def get_context_data(self, **kwargs):
        from billing.entitlements import Feature
        from billing.models import Plan

        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.filter(is_active=True)
        ctx["feature_labels"] = Feature.LABELS
        return ctx


class TermsView(PublicSiteMixin, TemplateView):
    template_name = "marketing/terms.html"


class PrivacyView(PublicSiteMixin, TemplateView):
    template_name = "marketing/privacy.html"


class SignupView(PublicSiteMixin, FormView):
    template_name = "marketing/signup.html"
    form_class = SignupForm

    def get_context_data(self, **kwargs):
        from billing.entitlements import Feature
        from billing.models import Plan

        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.filter(is_active=True)
        ctx["feature_labels"] = Feature.LABELS
        return ctx

    def get_initial(self):
        initial = super().get_initial()
        plan_slug = self.request.GET.get("plan")
        if plan_slug:
            from billing.models import Plan

            plan = Plan.objects.filter(slug=plan_slug, is_active=True).first()
            if plan:
                initial["plan"] = plan.pk
        return initial

    @transaction.atomic
    def form_valid(self, form):
        data = form.cleaned_data
        company = Company.objects.create(
            name=data["company_name"],
            subdomain=data["subdomain"],
            email=data["admin_email"],
            is_active=True,
        )
        User.objects.create_user(
            username=data["admin_username"],
            email=data["admin_email"],
            password=data["admin_password"],
            first_name=data["admin_first_name"],
            last_name=data["admin_last_name"],
            role=UserRole.SUPER_ADMIN,
            company=company,
        )
        plan = data["plan"]
        subscription = create_trial_subscription(company, plan)

        if stripe_enabled() and plan.stripe_price_id:
            success_url = tenant_absolute_url(
                company.subdomain,
                reverse("accounts:login") + "?welcome=1",
            )
            cancel_url = public_absolute_url(reverse("marketing:signup"))
            checkout_url = create_checkout_session(
                company,
                plan,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            messages.success(
                self.request,
                f"Workspace created! Complete payment to activate {plan.name}.",
            )
            return redirect(checkout_url)

        subscription.status = SubscriptionStatus.ACTIVE
        subscription.save(update_fields=["status", "updated_at"])
        messages.success(
            self.request,
            f"Your workspace is ready at {company.subdomain}.",
        )
        return redirect(tenant_absolute_url(company.subdomain, reverse("accounts:login")))


class SignupSuccessView(PublicSiteMixin, TemplateView):
    template_name = "marketing/signup_success.html"
