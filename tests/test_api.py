"""
Testes de rotas públicas e integração geral.

As rotas públicas (swagger, health) NÃO exigem autenticação.
Testes específicos por domínio estão em:
  - professionals/tests/test_api.py
  - appointments/tests/test_api.py
"""

import os

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

TEST_API_KEY = "test-api-key"


class PublicRoutesTest(TestCase):
    """Rotas públicas não exigem autenticação."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["API_KEY"] = TEST_API_KEY

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("API_KEY", None)
        super().tearDownClass()

    def test_health_check_is_public(self):
        response = APIClient().get("/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_is_public(self):
        response = APIClient().get("/swagger/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_is_public(self):
        response = APIClient().get("/redoc/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
