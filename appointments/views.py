from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.schemas import ERROR_401, ERROR_404

from .models import Appointment
from .schemas import ERROR_400_APPOINTMENT, ERROR_400_ID
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD de consultas médicas. Requer autenticação via X-API-KEY."""

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @swagger_auto_schema(
        operation_description="Lista todas as consultas agendadas.",
        responses={200: AppointmentSerializer(many=True), 401: ERROR_401},
        security=[{"API Key": []}],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Agenda uma nova consulta. Requer mínimo 30 min de antecedência.",
        responses={201: AppointmentSerializer, 400: ERROR_400_APPOINTMENT, 401: ERROR_401},
        security=[{"API Key": []}],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retorna uma consulta pelo ID.",
        responses={200: AppointmentSerializer, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza uma consulta.",
        responses={200: AppointmentSerializer, 400: ERROR_400_APPOINTMENT, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza campos específicos de uma consulta.",
        responses={200: AppointmentSerializer, 400: ERROR_400_APPOINTMENT, 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Cancela/remove uma consulta.",
        responses={204: "Excluída", 401: ERROR_401, 404: ERROR_404},
        security=[{"API Key": []}],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Lista consultas de um profissional específico.",
        responses={200: AppointmentSerializer(many=True), 400: ERROR_400_ID, 401: ERROR_401},
        security=[{"API Key": []}],
    )
    @action(detail=False, methods=["get"], url_path="professional/(?P<professional_id>[^/.]+)")
    def by_professional(self, request, professional_id=None):
        """Retorna consultas de um profissional específico."""
        try:
            professional_id = int(professional_id)
        except (ValueError, TypeError):
            return Response({"erro": "ID inválido"}, status=status.HTTP_400_BAD_REQUEST)

        appointments = Appointment.objects.filter(professional_id=professional_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
