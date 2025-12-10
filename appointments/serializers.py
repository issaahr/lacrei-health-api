from rest_framework import serializers
from django.utils import timezone
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Data da consulta não pode ser no passado")
        return value

    def validate_professional(self, value):
        if not value:
            raise serializers.ValidationError("Profissional é obrigatório")
        return value
