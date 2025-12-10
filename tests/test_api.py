import os
import json
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from professionals.models import Professional
from appointments.models import Appointment


class ProfessionalCRUDTest(APITestCase):
    """Testes de CRUD para profissionais."""

    def setUp(self):
        self.client = APIClient()
        self.professional_data = {
            'social_name': 'Dr. Maria Silva',
            'profession': 'Médica',
            'address': 'Rua das Flores, 123',
            'email': 'maria@teste.com',
            'phone': '11999999999'
        }

    def test_create_professional(self):
        """Testa criação de profissional."""
        response = self.client.post('/api/professionals/', self.professional_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 1)

    def test_list_professionals(self):
        """Testa listagem de profissionais."""
        Professional.objects.create(**self.professional_data)
        response = self.client.get('/api/professionals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_professional(self):
        """Testa atualização de profissional."""
        professional = Professional.objects.create(**self.professional_data)
        updated_data = self.professional_data.copy()
        updated_data['social_name'] = 'Dr. Maria Santos'
        response = self.client.put(f'/api/professionals/{professional.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        professional.refresh_from_db()
        self.assertEqual(professional.social_name, 'Dr. Maria Santos')

    def test_delete_professional(self):
        """Testa exclusão de profissional."""
        professional = Professional.objects.create(**self.professional_data)
        response = self.client.delete(f'/api/professionals/{professional.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)


class AppointmentCRUDTest(APITestCase):
    """Testes de CRUD para consultas."""

    def setUp(self):
        self.client = APIClient()
        self.professional = Professional.objects.create(
            social_name='Dr. João',
            profession='Psicólogo',
            address='Av. Brasil, 456',
            email='joao@teste.com',
            phone='11988888888'
        )
        self.appointment_date = timezone.now() + timedelta(days=7)

    def test_create_appointment(self):
        """Testa criação de consulta."""
        data = {
            'date': self.appointment_date.isoformat(),
            'professional': self.professional.id
        }
        response = self.client.post('/api/appointments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_list_appointments(self):
        """Testa listagem de consultas."""
        Appointment.objects.create(date=self.appointment_date, professional=self.professional)
        response = self.client.get('/api/appointments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_appointment(self):
        """Testa atualização de consulta."""
        appointment = Appointment.objects.create(date=self.appointment_date, professional=self.professional)
        new_date = timezone.now() + timedelta(days=14)
        response = self.client.patch(f'/api/appointments/{appointment.id}/', {'date': new_date.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_appointment(self):
        """Testa exclusão de consulta."""
        appointment = Appointment.objects.create(date=self.appointment_date, professional=self.professional)
        response = self.client.delete(f'/api/appointments/{appointment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)


class AppointmentByProfessionalTest(APITestCase):
    """Testa busca de consultas por profissional."""

    def setUp(self):
        self.client = APIClient()
        self.professional1 = Professional.objects.create(
            social_name='Dr. Ana',
            profession='Dermatologista',
            address='Rua A, 1',
            email='ana@teste.com',
            phone='11977777777'
        )
        self.professional2 = Professional.objects.create(
            social_name='Dr. Pedro',
            profession='Cardiologista',
            address='Rua B, 2',
            email='pedro@teste.com',
            phone='11966666666'
        )
        future_date = timezone.now() + timedelta(days=7)
        Appointment.objects.create(date=future_date, professional=self.professional1)
        Appointment.objects.create(date=future_date + timedelta(days=1), professional=self.professional1)
        Appointment.objects.create(date=future_date, professional=self.professional2)

    def test_list_appointments_by_professional(self):
        """Testa listagem de consultas por ID do profissional."""
        response = self.client.get(f'/api/appointments/professional/{self.professional1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_appointments_invalid_professional_id(self):
        """Testa erro com ID inválido."""
        response = self.client.get('/api/appointments/professional/abc/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ValidationErrorTest(APITestCase):
    """Testes de erro de validação."""

    def setUp(self):
        self.client = APIClient()
        self.professional = Professional.objects.create(
            social_name='Dr. Teste',
            profession='Médico',
            address='Rua Teste, 123',
            email='teste@teste.com',
            phone='11999999999'
        )

    def test_create_professional_missing_fields(self):
        """Testa erro ao criar profissional sem campos obrigatórios."""
        response = self.client.post('/api/professionals/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professional_invalid_email(self):
        """Testa erro ao criar profissional com email inválido."""
        data = {
            'social_name': 'Dr. Teste',
            'profession': 'Médico',
            'address': 'Rua Teste, 123',
            'email': 'email-invalido',
            'phone': '11999999999'
        }
        response = self.client.post('/api/professionals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professional_invalid_phone(self):
        """Testa erro ao criar profissional com telefone inválido."""
        data = {
            'social_name': 'Dr. Teste',
            'profession': 'Médico',
            'address': 'Rua Teste, 123',
            'email': 'teste@teste.com',
            'phone': 'abc123'
        }
        response = self.client.post('/api/professionals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_missing_professional(self):
        """Testa erro ao criar consulta sem profissional."""
        data = {
            'date': (timezone.now() + timedelta(days=7)).isoformat()
        }
        response = self.client.post('/api/appointments/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_past_date(self):
        """Testa erro ao criar consulta com data no passado."""
        data = {
            'date': (timezone.now() - timedelta(days=1)).isoformat(),
            'professional': self.professional.id
        }
        response = self.client.post('/api/appointments/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_invalid_professional(self):
        """Testa erro ao criar consulta com profissional inexistente."""
        data = {
            'date': (timezone.now() + timedelta(days=7)).isoformat(),
            'professional': 99999
        }
        response = self.client.post('/api/appointments/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APIKeyAuthenticationTest(TestCase):
    """Testa autenticação via API Key."""

    def setUp(self):
        self.original_api_key = os.environ.get('API_KEY', '')

    def tearDown(self):
        os.environ['API_KEY'] = self.original_api_key

    def test_access_without_api_key(self):
        """Testa erro ao acessar sem API Key quando configurada."""
        os.environ['API_KEY'] = 'test-api-key'

        from app.middleware import APIKeyMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/api/professionals/')

        middleware = APIKeyMiddleware(lambda r: None)
        response = middleware(request)

        self.assertEqual(response.status_code, 401)
        self.assertIn('erro', json.loads(response.content))

    def test_access_with_valid_api_key(self):
        """Testa acesso com API Key válida."""
        os.environ['API_KEY'] = 'test-api-key'

        from app.middleware import APIKeyMiddleware
        from django.test import RequestFactory
        from django.http import HttpResponse

        factory = RequestFactory()
        request = factory.get('/api/professionals/', HTTP_X_API_KEY='test-api-key')

        def get_response(r):
            return HttpResponse('OK')

        middleware = APIKeyMiddleware(get_response)
        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    def test_access_with_invalid_api_key(self):
        """Testa erro ao acessar com API Key inválida."""
        os.environ['API_KEY'] = 'test-api-key'

        from app.middleware import APIKeyMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/api/professionals/', HTTP_X_API_KEY='chave-errada')

        middleware = APIKeyMiddleware(lambda r: None)
        response = middleware(request)

        self.assertEqual(response.status_code, 401)

    def test_exempt_paths_allowed(self):
        """Testa que paths isentos não precisam de API Key."""
        os.environ['API_KEY'] = 'test-api-key'

        from app.middleware import APIKeyMiddleware
        from django.test import RequestFactory
        from django.http import HttpResponse

        factory = RequestFactory()

        def get_response(r):
            return HttpResponse('OK')

        middleware = APIKeyMiddleware(get_response)

        for path in ['/swagger/', '/redoc/', '/health/']:
            request = factory.get(path)
            response = middleware(request)
            self.assertEqual(response.status_code, 200, f"Path {path} deveria ser permitido")
