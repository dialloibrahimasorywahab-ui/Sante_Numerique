from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from .models import Service
from .serviceRepositories import ServiceRepository


class ServicesProjectConfigTests(SimpleTestCase):
    def test_services_app_is_registered(self):
        self.assertTrue(apps.is_installed('services'))

    def test_services_routes_are_available(self):
        self.assertEqual(resolve('/services/').view_name, 'create_service')
        self.assertEqual(resolve('/services/all/').view_name, 'get_all_services')


class ServiceRepositoryTests(TestCase):
    def test_create_and_get_service(self):
        repository = ServiceRepository()
        service = repository.createService(
            nomService=Service.NomService.CARDIOLOGIE,
            description="Service des maladies cardiovasculaires"
        )
        self.assertIsNotNone(service.idService)
        self.assertEqual(service.nomService, Service.NomService.CARDIOLOGIE)

        fetched = repository.get_service(service.idService)
        self.assertEqual(fetched, service)

    def test_create_service_api(self):
        client = APIClient()
        payload = {
            "nomService": "PEDIATRIE",
            "description": "Soins pédiatriques",
        }
        response = client.post("/services/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nomService"], "PEDIATRIE")

    def test_create_service_empty_body_returns_400(self):
        client = APIClient()
        response = client.post("/services/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("nomService", response.data)

    def test_create_service_api_display_name(self):
        client = APIClient()
        payload = {
            "nomService": "Chirurgie Générale",
            "description": "Bloc opératoire et interventions"
        }
        response = client.post("/services/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nomService"], "CHIRURGIE")
        self.assertEqual(response.data["nomServiceDisplay"], "Chirurgie Générale")


