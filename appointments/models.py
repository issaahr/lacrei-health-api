from django.db import models
from django.utils import timezone

from professionals.models import Professional


class Appointment(models.Model):
    date = models.DateTimeField()
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name="appointments")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
