from django.db import models
from django.utils import timezone

from professionals.models import Professional


class Appointment(models.Model):
    """Modelo para consultas/agendamentos médicos."""

    date = models.DateTimeField()
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["professional", "date"], name="unique_appointment_professional_date")
        ]

    def __str__(self):
        return f"Consulta com {self.professional.social_name} em {self.date.strftime('%d/%m/%Y %H:%M')}"
