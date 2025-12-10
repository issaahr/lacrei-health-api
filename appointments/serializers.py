from rest_framework import serializers
from django.utils import timezone
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer para consultas médicas com validações."""

    class Meta:
        model = Appointment
        fields = ['id', 'date', 'professional']
        read_only_fields = ['id']

    def validate_date(self, value):
        """Valida que a data não está no passado."""
        if value < timezone.now():
            raise serializers.ValidationError("Data da consulta não pode ser no passado")
        return value

    def validate_professional(self, value):
        """Valida que o profissional foi informado."""
        if not value:
            raise serializers.ValidationError("Profissional é obrigatório")
        return value
