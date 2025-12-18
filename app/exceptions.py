from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Handler customizado para converter erros de banco em 400."""

    # Primeiro, chama o handler padrão do DRF
    response = exception_handler(exc, context)

    # Se o DRF não tratou, verifica se é IntegrityError
    if response is None and isinstance(exc, IntegrityError):
        return Response({"erro": "Registro duplicado ou violação de constraint"}, status=status.HTTP_400_BAD_REQUEST)

    return response
