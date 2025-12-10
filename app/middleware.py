import logging
from django.http import JsonResponse
from decouple import config

logger = logging.getLogger('api')


class APIKeyMiddleware:
    """Middleware para autenticação via API Key."""
    EXEMPT_PATHS = ['/swagger/', '/redoc/', '/schema/', '/health/']

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = config('API_KEY', default='')

    def __call__(self, request):
        logger.debug(f"{request.method} {request.path} - IP: {self.get_client_ip(request)}")

        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return self.get_response(request)

        if not self.api_key:
            return self.get_response(request)

        request_key = request.headers.get('X-API-KEY', '')
        if request_key != self.api_key:
            logger.warning(f"API Key inválida - IP: {self.get_client_ip(request)}")
            return JsonResponse({'erro': 'API Key inválida ou ausente'}, status=401)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

