from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Appointment

# Constantes de validação
MIN_ADVANCE_MINUTES = 30
MAX_FUTURE_DAYS = 365
APPOINTMENT_INTERVAL_MINUTES = 60


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer para consultas médicas."""

    class Meta:
        model = Appointment
        fields = ["id", "date", "professional", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "professional": {
                "error_messages": {
                    "does_not_exist": "Profissional não encontrado.",
                    "null": "Este campo é obrigatório.",
                    "required": "Este campo é obrigatório.",
                }
            }
        }

    def validate_date(self, value):
        """Data deve ser no futuro com antecedência mínima."""
        now = timezone.now()

        if value < now:
            raise serializers.ValidationError("Data não pode ser no passado")

        if value < now + timedelta(minutes=MIN_ADVANCE_MINUTES):
            raise serializers.ValidationError(f"Mínimo {MIN_ADVANCE_MINUTES} minutos de antecedência")

        if value > now + timedelta(days=MAX_FUTURE_DAYS):
            raise serializers.ValidationError(f"Máximo {MAX_FUTURE_DAYS} dias no futuro")

        return value

    def validate(self, attrs):
        """Verifica conflito de horário."""
        date = attrs.get("date")
        professional = attrs.get("professional")

        if not date or not professional:
            return attrs

        conflicting = Appointment.objects.filter(
            professional=professional,
            date__gte=date - timedelta(minutes=APPOINTMENT_INTERVAL_MINUTES),
            date__lt=date + timedelta(minutes=APPOINTMENT_INTERVAL_MINUTES),
        )

        if self.instance:
            conflicting = conflicting.exclude(pk=self.instance.pk)

        if conflicting.exists():
            raise serializers.ValidationError(
                {"date": f"Conflito de horário (intervalo mínimo: {APPOINTMENT_INTERVAL_MINUTES} min)"}
            )

        return attrs
