"""
Testes da API de Consultas/Agendamentos.

Cada endpoint testa: Auth (401) → Validação (400) → Sucesso (2xx)
"""

import os
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from appointments.models import Appointment
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
# GET /api/appointments/
# =============================================================================
class ListAppointmentsTest(BaseAPITest):
    """GET /api/appointments/ - Listar consultas."""

    def setUp(self):
        self.url = "/api/appointments/"
        self.professional = Professional.objects.create(
            social_name="Dr. João",
            profession="Psicólogo",
            address="Rua Teste, 123",
            email="joao@teste.com",
            phone="+5511988888888",
        )
        self.appointment = Appointment.objects.create(
            date=timezone.now() + timedelta(days=7),
            professional=self.professional,
        )

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_200_with_list(self):
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


# =============================================================================
# POST /api/appointments/
# =============================================================================
class CreateAppointmentTest(BaseAPITest):
    """POST /api/appointments/ - Agendar consulta."""

    def setUp(self):
        self.url = "/api/appointments/"
        self.professional = Professional.objects.create(
            social_name="Dr. João",
            profession="Psicólogo",
            address="Rua Teste, 123",
            email="joao@teste.com",
            phone="+5511988888888",
        )
        self.future_date = timezone.now() + timedelta(days=7)
        self.valid_data = {
            "date": self.future_date.isoformat(),
            "professional": self.professional.id,
        }

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Validação ---
    def test_returns_400_for_past_date(self):
        data = {**self.valid_data, "date": (timezone.now() - timedelta(days=1)).isoformat()}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_returns_400_for_too_soon(self):
        data = {**self.valid_data, "date": (timezone.now() + timedelta(minutes=10)).isoformat()}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_returns_400_for_too_far(self):
        data = {**self.valid_data, "date": (timezone.now() + timedelta(days=400)).isoformat()}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_returns_400_for_invalid_professional(self):
        data = {**self.valid_data, "professional": 99999}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_for_conflicting_time(self):
        self.get_client().post(self.url, self.valid_data)
        data = {**self.valid_data, "date": (self.future_date + timedelta(minutes=30)).isoformat()}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    # --- Sucesso ---
    def test_returns_201_with_valid_data(self):
        response = self.get_client().post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_allows_same_time_different_professional(self):
        self.get_client().post(self.url, self.valid_data)
        professional2 = Professional.objects.create(
            social_name="Dr. Outro",
            profession="Médico",
            address="Rua Outra, 456",
            email="outro@teste.com",
            phone="+5511977777777",
        )
        data = {**self.valid_data, "professional": professional2.id}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_allows_sufficient_time_gap(self):
        self.get_client().post(self.url, self.valid_data)
        data = {**self.valid_data, "date": (self.future_date + timedelta(hours=2)).isoformat()}
        response = self.get_client().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# =============================================================================
# GET /api/appointments/{id}/
# =============================================================================
class RetrieveAppointmentTest(BaseAPITest):
    """GET /api/appointments/{id}/ - Detalhar consulta."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. João",
            profession="Psicólogo",
            address="Rua Teste, 123",
            email="joao@teste.com",
            phone="+5511988888888",
        )
        self.appointment = Appointment.objects.create(
            date=timezone.now() + timedelta(days=7),
            professional=self.professional,
        )
        self.url = f"/api/appointments/{self.appointment.id}/"

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_200_with_data(self):
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["professional"], self.professional.id)


# =============================================================================
# DELETE /api/appointments/{id}/
# =============================================================================
class DeleteAppointmentTest(BaseAPITest):
    """DELETE /api/appointments/{id}/ - Cancelar consulta."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. João",
            profession="Psicólogo",
            address="Rua Teste, 123",
            email="joao@teste.com",
            phone="+5511988888888",
        )
        self.appointment = Appointment.objects.create(
            date=timezone.now() + timedelta(days=7),
            professional=self.professional,
        )
        self.url = f"/api/appointments/{self.appointment.id}/"

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Sucesso ---
    def test_returns_204_on_delete(self):
        response = self.get_client().delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# =============================================================================
# GET /api/appointments/professional/{id}/
# =============================================================================
class ListAppointmentsByProfessionalTest(BaseAPITest):
    """GET /api/appointments/professional/{id}/ - Consultas por profissional."""

    def setUp(self):
        self.professional = Professional.objects.create(
            social_name="Dr. João",
            profession="Psicólogo",
            address="Rua Teste, 123",
            email="joao@teste.com",
            phone="+5511988888888",
        )
        self.url = f"/api/appointments/professional/{self.professional.id}/"
        future = timezone.now() + timedelta(days=7)
        Appointment.objects.create(date=future, professional=self.professional)
        Appointment.objects.create(date=future + timedelta(days=1), professional=self.professional)

    # --- Auth ---
    def test_returns_401_without_api_key(self):
        response = self.get_client(authenticated=False).get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Validação ---
    def test_returns_400_for_invalid_id(self):
        response = self.get_client().get("/api/appointments/professional/abc/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Sucesso ---
    def test_returns_200_with_filtered_list(self):
        response = self.get_client().get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
