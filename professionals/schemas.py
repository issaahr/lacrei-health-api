"""Schemas de erro para documentação Swagger - Profissionais."""

from drf_yasg import openapi

ERROR_400_PROFESSIONAL = openapi.Response(
    description="Erro de validação",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "social_name": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Mínimo 3 caracteres", "Nome inválido"],
            ),
            "email": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Email já cadastrado", "Insira um endereço de email válido."],
            ),
            "phone": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Telefone inválido", "Formato de telefone inválido"],
            ),
            "profession": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Mínimo 3 caracteres"],
            ),
            "address": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Mínimo 5 caracteres"],
            ),
        },
    ),
)
