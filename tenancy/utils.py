import re

from django.conf import settings

SUBDOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
RESERVED_SUBDOMAINS = frozenset(
    {
        "www",
        "app",
        "api",
        "admin",
        "mail",
        "smtp",
        "ftp",
        "staging",
        "dev",
        "test",
        "demo",
        "support",
        "help",
        "status",
        "billing",
    }
)


def normalize_host(host: str) -> str:
    return host.split(":")[0].lower().strip()


def parse_subdomain(host: str) -> str | None:
    host = normalize_host(host)
    base = settings.TENANT_BASE_DOMAIN.lower()

    if host == base or host == f"www.{base}":
        return None

    suffix = f".{base}"
    if not host.endswith(suffix):
        return None

    subdomain = host[: -len(suffix)]
    if not subdomain or "." in subdomain:
        return None
    return subdomain


def is_public_host(host: str) -> bool:
    return parse_subdomain(host) is None


def tenant_absolute_url(subdomain: str, path: str = "/") -> str:
    base = settings.TENANT_BASE_DOMAIN
    scheme = settings.TENANT_URL_SCHEME
    port = settings.TENANT_PORT
    host = f"{subdomain}.{base}"
    if port:
        host = f"{host}:{port}"
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{scheme}://{host}{path}"


def public_absolute_url(path: str = "/") -> str:
    base = settings.TENANT_BASE_DOMAIN
    scheme = settings.TENANT_URL_SCHEME
    port = settings.TENANT_PORT
    host = base
    if port:
        host = f"{host}:{port}"
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{scheme}://{host}{path}"


def validate_subdomain(subdomain: str) -> str | None:
    value = subdomain.lower().strip()
    if not value:
        return "Subdomain is required."
    if len(value) < 3:
        return "Subdomain must be at least 3 characters."
    if value in RESERVED_SUBDOMAINS:
        return "This subdomain is reserved."
    if not SUBDOMAIN_RE.match(value):
        return "Use lowercase letters, numbers, and hyphens only."
    return None
