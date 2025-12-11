from django.db import models

from professionals.models import Professional


class Appointment(models.Model):
    date = models.DateTimeField()
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    class Meta:
        db_table = 'appointments'

