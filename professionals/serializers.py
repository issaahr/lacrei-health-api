from rest_framework import serializers
from .models import Professional
import re


class ProfessionalSerializer(serializers.ModelSerializer):
    social_name = serializers.CharField(max_length=255, min_length=2)
    profession = serializers.CharField(max_length=100, min_length=2)
    address = serializers.CharField(max_length=255, min_length=5)
    email = serializers.EmailField(max_length=255)
    phone = serializers.CharField(max_length=20, min_length=8)

    class Meta:
        model = Professional
        fields = '__all__'

    def validate_social_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Nome social não pode ser vazio")
        return value

    def validate_profession(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Profissão não pode ser vazia")
        return value

    def validate_address(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Endereço não pode ser vazio")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not re.match(r'^[\d\s\-\(\)\+]+$', value):
            raise serializers.ValidationError("Telefone deve conter apenas números e caracteres válidos")
        return value
