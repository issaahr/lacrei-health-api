"""
Testes da API de Profissionais.

Cada endpoint testa: Auth (401) → Validação (400) → Sucesso (2xx)
"""

import os

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from professionals.models import Professional

TEST_API_KEY = "test-api-key"


class BaseAPITest(APITestCase):
    """Classe base com helpers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["API_KEY"] = TEST_API_KEY

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("API_KEY", None)
        super().tearDownClass()

    def get_client(self, authenticated=True):
        client = APIClient()
        if authenticated:
            client.credentials(HTTP_X_API_KEY=TEST_API_KEY)
        return client


# =============================================================================
# GET /api/professionals/
# =============================================================================
class ListProfessionalsTest(BaseAPITest):
    """GET /api/professionals/ - Listar profissionais."""

    def setUp(self):
        self.url = "/api/professionals/"
        self.professional = Professional.objects.create(
            social_name="Dr. Maria",
            profession="Médica",
            address="Rua Teste, 123",
            email="maria@teste.com",
            phone="+5511999999999",
        )

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_401_with_invalid_api_key(self):
        client = APIClient()
        client.credentials(HTTP_X_API_KEY="chave-invalida")
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_200_with_list(self):
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_returns_empty_list_when_no_data(self):
        Professional.objects.all().delete()
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


# =============================================================================
# POST /api/professionals/
# =============================================================================
class CreateProfessionalTest(BaseAPITest):
    """POST /api/professionals/ - Criar profissional."""

    def setUp(self):
        self.url = "/api/professionals/"
        self.valid_data = {
            "social_name": "Dr. Maria Silva",
            "profession": "Médica",
            "address": "Rua das Flores, 123",
            "email": "maria@teste.com",
            "phone": "11999999999",
        }

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Validação ---
    def test_returns_400_when_missing_fields(self):
        response = self.get_client().post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_for_invalid_email(self):
        data = {**self.valid_data, "email": "email-invalido"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_returns_400_for_duplicate_email(self):
        self.get_client().post(self.url, self.valid_data)
        data = {**self.valid_data, "social_name": "Dr. João"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_returns_400_for_invalid_phone(self):
        data = {**self.valid_data, "phone": "abc123", "email": "novo@teste.com"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_returns_400_for_name_with_numbers(self):
        data = {**self.valid_data, "social_name": "12345", "email": "novo@teste.com"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.data)

    # --- Sucesso ---
    def test_returns_201_with_valid_data(self):
        response = self.get_client().post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)

    def test_normalizes_phone_to_e164(self):
        data = {**self.valid_data, "phone": "(11) 99999-9999"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["phone"].startswith("+55"))

    def test_allows_special_chars_in_name(self):
        data = {**self.valid_data, "social_name": "Maria D'Ávila-Santos", "email": "davila@teste.com"}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# =============================================================================
# GET /api/professionals/{id}/
# =============================================================================
class RetrieveProfessionalTest(BaseAPITest):
    """GET /api/professionals/{id}/ - Detalhar profissional."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. Maria",
            profession="Médica",
            address="Rua Teste, 123",
            email="maria@teste.com",
            phone="+5511999999999",
        )
        self.url = f"/api/professionals/{self.professional.id}/"

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Erro ---
    def test_returns_404_for_nonexistent(self):
        response = self.get_client().get("/api/professionals/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Sucesso ---
    def test_returns_200_with_data(self):
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.professional.email)


# =============================================================================
# PUT /api/professionals/{id}/
# =============================================================================
class UpdateProfessionalTest(BaseAPITest):
    """PUT /api/professionals/{id}/ - Atualizar profissional."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. Maria",
            profession="Médica",
            address="Rua Teste, 123",
            email="maria@teste.com",
            phone="+5511999999999",
        )
        self.url = f"/api/professionals/{self.professional.id}/"
        self.valid_data = {
            "social_name": "Dr. Maria Santos",
            "profession": "Cardiologista",
            "address": "Rua Nova, 456",
            "email": "maria@teste.com",
            "phone": "11999999999",
        }

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).put(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_200_on_update(self):
        response = self.get_client().put(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["social_name"], "Dr. Maria Santos")

    def test_allows_keeping_same_email(self):
        response = self.get_client().put(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# =============================================================================
# DELETE /api/professionals/{id}/
# =============================================================================
class DeleteProfessionalTest(BaseAPITest):
    """DELETE /api/professionals/{id}/ - Excluir profissional."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. Maria",
            profession="Médica",
            address="Rua Teste, 123",
            email="maria@teste.com",
            phone="+5511999999999",
        )
        self.url = f"/api/professionals/{self.professional.id}/"

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_204_on_delete(self):
        response = self.get_client().delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)
