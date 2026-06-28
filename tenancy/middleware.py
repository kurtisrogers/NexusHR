from django.conf import settings
from django.http import Http404
from django.urls import set_urlconf

from organization.models import Company

from .utils import is_public_host, parse_subdomain, public_absolute_url


class TenantMiddleware:
    """Resolve tenant from subdomain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        request.is_public_site = is_public_host(host)
        request.tenant = None

        if not request.is_public_site:
            subdomain = parse_subdomain(host)
            if subdomain:
                try:
                    request.tenant = Company.objects.get(subdomain=subdomain, is_active=True)
                    request.is_public_site = False
                except Company.DoesNotExist as exc:
                    raise Http404("Organization not found.") from exc

        set_urlconf(settings.ROOT_URLCONF)
        response = self.get_response(request)
        return response


class PublicSiteRedirectMiddleware:
    """Redirect tenant-only paths accessed on the public domain to signup."""

    TENANT_ONLY_PREFIXES = (
        "/employees/",
        "/organization/",
        "/leave/",
        "/attendance/",
        "/recruitment/",
        "/performance/",
        "/payroll/",
        "/expenses/",
        "/announcements/",
        "/reports/",
        "/billing/",
        "/accounts/login",
        "/accounts/logout",
        "/accounts/users",
        "/accounts/password-reset",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.is_public_site and not request.path.startswith("/admin/"):
            for prefix in self.TENANT_ONLY_PREFIXES:
                if request.path.startswith(prefix):
                    return redirect_response(public_absolute_url("/signup/"))
        return self.get_response(request)


def redirect_response(url):
    from django.shortcuts import redirect

    return redirect(url)
