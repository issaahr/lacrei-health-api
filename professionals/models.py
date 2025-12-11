from django.db import models
from django.utils import timezone


class Professional(models.Model):
    social_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "professionals"
