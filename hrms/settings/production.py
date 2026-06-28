import os

from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() in {"1", "true", "yes"}

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],  # noqa: F405
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "nexushr"),
        "USER": os.environ.get("DB_USER", "nexushr"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() in {"1", "true", "yes"}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
TENANT_URL_SCHEME = os.environ.get("TENANT_URL_SCHEME", "https")
TENANT_PORT = os.environ.get("TENANT_PORT", "")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
