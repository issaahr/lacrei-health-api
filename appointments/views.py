from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de consultas médicas."""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @action(detail=False, methods=['get'], url_path='professional/(?P<professional_id>[^/.]+)')
    def by_professional(self, request, professional_id=None):
        """Retorna consultas de um profissional específico."""
        try:
            professional_id = int(professional_id)
        except (ValueError, TypeError):
            return Response(
                {'erro': 'ID do profissional deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointments = Appointment.objects.filter(professional_id=professional_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
