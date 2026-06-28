from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect

from billing.entitlements import has_feature


class TenantRequiredMixin:
    """Require a resolved tenant subdomain for tenant app views."""

    def dispatch(self, request, *args, **kwargs):
        if request.is_public_site or not request.tenant:
            raise Http404("This page is only available on your organization subdomain.")
        return super().dispatch(request, *args, **kwargs)


class TenantLoginRequiredMixin(TenantRequiredMixin, LoginRequiredMixin):
    pass


class TenantUserRequiredMixin(TenantLoginRequiredMixin):
    """Ensure authenticated user belongs to the current tenant."""

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.tenant
            and request.user.company_id != request.tenant.id
        ):
            messages.error(request, "Your account does not belong to this organization.")
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)


class FeatureRequiredMixin(TenantUserRequiredMixin):
    required_feature: str | None = None

    def dispatch(self, request, *args, **kwargs):
        if (
            self.required_feature
            and request.tenant
            and not has_feature(request.tenant, self.required_feature)
        ):
            messages.warning(
                request,
                "This feature is not included in your current plan. Upgrade to unlock it.",
            )
            return redirect("billing:settings")
        return super().dispatch(request, *args, **kwargs)


class TenantObjectMixin:
    tenant_lookup_field = "pk"

    def get_queryset(self):
        from tenancy.scoping import get_scope

        scope = get_scope(self.request)
        if hasattr(scope, f"{self.model._meta.model_name}s"):
            method = getattr(scope, f"{self.model._meta.model_name}s")
            return method()
        qs = super().get_queryset()
        if hasattr(self.model, "company"):
            return qs.filter(company=self.request.tenant)
        return qs
