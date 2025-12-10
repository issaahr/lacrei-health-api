from django.db import models


class Professional(models.Model):
    social_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'professionals'
