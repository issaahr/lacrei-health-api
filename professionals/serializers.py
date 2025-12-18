import re

import phonenumbers
from rest_framework import serializers

from .models import Professional

# Constantes de validação
MIN_NAME_LENGTH = 3
MIN_PROFESSION_LENGTH = 3
MIN_ADDRESS_LENGTH = 5


class ProfessionalSerializer(serializers.ModelSerializer):
    """Serializer para profissionais de saúde."""

    class Meta:
        model = Professional
        fields = ["id", "social_name", "profession", "address", "email", "phone", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_social_name(self, value):
        """Nome deve conter apenas letras, espaços, apóstrofos, hífens e pontos."""
        value = value.strip()
        if len(value) < MIN_NAME_LENGTH:
            raise serializers.ValidationError(f"Mínimo {MIN_NAME_LENGTH} caracteres")
        # Permite: letras, espaços, apóstrofos, hífens e pontos (Dr., Dra.)
        if not re.match(r"^[A-Za-zÀ-ÿ\s'\-\.]+$", value):
            raise serializers.ValidationError("Nome inválido")
        return value

    def validate_profession(self, value):
        """Profissão deve conter apenas letras."""
        value = value.strip()
        if len(value) < MIN_PROFESSION_LENGTH:
            raise serializers.ValidationError(f"Mínimo {MIN_PROFESSION_LENGTH} caracteres")
        if not re.match(r"^[A-Za-zÀ-ÿ\s\-]+$", value):
            raise serializers.ValidationError("Profissão deve conter apenas letras")
        return value

    def validate_address(self, value):
        """Valida e sanitiza endereço."""
        value = value.strip()
        if len(value) < MIN_ADDRESS_LENGTH:
            raise serializers.ValidationError(f"Mínimo {MIN_ADDRESS_LENGTH} caracteres")
        return value

    def validate_phone(self, value):
        """Valida e normaliza telefone brasileiro."""
        value = value.strip()
        cleaned = re.sub(r"[\s\-\(\)]", "", value)

        if not cleaned.startswith("+"):
            cleaned = "+55" + cleaned

        try:
            parsed = phonenumbers.parse(cleaned, "BR")
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Telefone inválido")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Formato de telefone inválido")

    def validate_email(self, value):
        """Verifica unicidade do email (case-insensitive)."""
        value = value.strip().lower()
        queryset = Professional.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Email já cadastrado")
        return value
