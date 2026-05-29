from django.utils.deprecation import MiddlewareMixin
from .models import Organization


class TenantMiddleware(MiddlewareMixin):
    """Simple tenant middleware that sets `request.tenant` based on X-Tenant header.

    This is intentionally minimal for a prototype. In production you'd have
    robust tenant discovery and error handling.
    """

    def process_request(self, request):
        tenant_key = request.META.get("HTTP_X_TENANT")
        request.tenant = None
        if tenant_key:
            try:
                request.tenant = Organization.objects.get(name=tenant_key)
            except Organization.DoesNotExist:
                request.tenant = None
