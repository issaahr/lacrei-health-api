from django.db import models
from django.utils import timezone


class Professional(models.Model):
    """Modelo para profissionais de saúde."""

    social_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "professionals"

    def __str__(self):
        return f"{self.social_name} - {self.profession}"
