import logging
import os

from django.http import JsonResponse

logger = logging.getLogger('api')


class APIKeyMiddleware:
    """Middleware para autenticação via API Key."""
    EXEMPT_PATHS = ['/swagger/', '/redoc/', '/schema/', '/health/', '/static/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug(f"{request.method} {request.path} - IP: {self.get_client_ip(request)}")

        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return self.get_response(request)

        api_key = os.environ.get('API_KEY', '')
        if not api_key:
            return self.get_response(request)

        request_key = request.headers.get('X-API-KEY', '')
        if request_key != api_key:
            logger.warning(f"API Key inválida - IP: {self.get_client_ip(request)}")
            return JsonResponse({'erro': 'API Key inválida ou ausente'}, status=401)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
