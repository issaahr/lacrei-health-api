"""Schemas de erro para documentação Swagger - Consultas."""

from drf_yasg import openapi

ERROR_400_APPOINTMENT = openapi.Response(
    description="Erro de validação",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "date": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=[
                    "Data não pode ser no passado",
                    "Mínimo 30 minutos de antecedência",
                    "Máximo 365 dias no futuro",
                    "Conflito de horário com outra consulta",
                ],
            ),
            "professional": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Este campo é obrigatório.", "Profissional não encontrado."],
            ),
        },
    ),
)

ERROR_400_ID = openapi.Response(
    description="ID inválido",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"erro": openapi.Schema(type=openapi.TYPE_STRING, example="ID inválido")},
    ),
)
