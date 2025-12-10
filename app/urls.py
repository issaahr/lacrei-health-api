from django.urls import path, include
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

API_INFO = openapi.Info(
    title="Lacrei Health API",
    default_version='v1',
    description="API para gerenciamento de profissionais de saúde e consultas médicas.",
    contact=openapi.Contact(email="contato@teste.com.br"),
)


def health_check(request):
    """Endpoint para verificação do status da API."""
    return JsonResponse({'status': 'ok'})


schema_view = get_schema_view(
    API_INFO,
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    path('health/', health_check),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    path('schema/', schema_view.without_ui(cache_timeout=0)),
    path('api/', include('professionals.urls')),
    path('api/', include('appointments.urls')),
]
