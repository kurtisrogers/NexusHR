from django.http import JsonResponse


def healthz(_request):
    """Lightweight health check for load balancers (no DB or tenant context)."""
    return JsonResponse({"status": "ok"})
