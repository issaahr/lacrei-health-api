"""Schemas de erro compartilhados para documentação Swagger."""

from drf_yasg import openapi

ERROR_401 = openapi.Response(
    description="Não autorizado",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"erro": openapi.Schema(type=openapi.TYPE_STRING, example="API Key não fornecida")},
    ),
)

ERROR_404 = openapi.Response(
    description="Não encontrado",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"detail": openapi.Schema(type=openapi.TYPE_STRING, example="Não encontrado.")},
    ),
)
