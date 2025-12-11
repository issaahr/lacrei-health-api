from rest_framework import viewsets

from .models import Professional
from .serializers import ProfessionalSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de profissionais de saúde."""

    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
