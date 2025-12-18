from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

from app.schemas import ERROR_401, ERROR_404

from .models import Professional
from .schemas import ERROR_400_PROFESSIONAL
from .serializers import ProfessionalSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    """CRUD de profissionais de saúde. Requer autenticação via X-API-KEY."""

    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer

    @swagger_auto_schema(
        operation_description="Lista todos os profissionais cadastrados.",
        responses={200: ProfessionalSerializer(many=True), 401: ERROR_401},
        security=[{"API Key": []}],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Cria um novo profissional.",
        responses={201: ProfessionalSerializer, 400: ERROR_400_PROFESSIONAL, 401: ERROR_401},
        security=[{"API Key": []}],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retorna um profissional pelo ID.",
        responses={200: ProfessionalSerializer, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza todos os campos de um profissional.",
        responses={200: ProfessionalSerializer, 400: ERROR_400_PROFESSIONAL, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza campos específicos de um profissional.",
        responses={200: ProfessionalSerializer, 400: ERROR_400_PROFESSIONAL, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Remove um profissional. Consultas associadas também serão excluídas.",
        responses={204: "Excluído", 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
