from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from .models import Batiment
from .batimentRepositories import BatimentRepository
from .batimentServices import BatimentService
from chambre.models import Chambre


class BatimentConfigTests(SimpleTestCase):
    def test_batiment_app_is_installed(self):
        self.assertTrue(apps.is_installed('batiment'))

    def test_batiment_routes_are_available(self):
        self.assertEqual(resolve('/batiments/').view_name, 'create_batiment')
        self.assertEqual(resolve('/batiments/all/').view_name, 'get_all_batiments')


class BatimentModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.repository = BatimentRepository()
        self.service = BatimentService()

    def test_create_and_get_batiment(self):
        batiment = self.repository.create_batiment(
            nom="Bâtiment principal",
            description="Consultations et médecine générale",
            nombre_chambre=10
        )
        self.assertIsNotNone(batiment.idBatiment)
        self.assertEqual(str(batiment), "Bâtiment principal (10 chambres)")

        fetched = self.repository.get_batiment(batiment.idBatiment)
        self.assertEqual(fetched, batiment)

    def test_get_by_nom_and_search(self):
        self.repository.create_batiment(nom="Pavillon Urgences", description="Réanimation")
        self.repository.create_batiment(nom="Bloc Opératoire", description="Chirurgie")

        found = self.repository.get_batiment_by_nom("pavillon urgences")
        self.assertIsNotNone(found)
        self.assertEqual(found.nom, "Pavillon Urgences")

        results = self.repository.search_batiments("Chirurgie")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].nom, "Bloc Opératoire")

    def test_seed_default_batiments(self):
        created = self.service.seed_default_batiments()
        self.assertGreaterEqual(len(created), 5)
        self.assertTrue(Batiment.objects.filter(nom="Bâtiment Principal A").exists())


class BatimentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.batiment = Batiment.objects.create(
            nom="Bâtiment A",
            description="Aile Est",
            nombre_chambre=5
        )

    def test_create_batiment_api(self):
        payload = {
            "nom": "Bâtiment B",
            "description": "Aile Ouest",
            "nombre_chambre": 12
        }
        response = self.client.post("/batiments/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Bâtiment B")
        self.assertEqual(response.data["nombre_chambre"], 12)

    def test_create_batiment_duplicate_name_returns_400(self):
        payload = {"nom": "Bâtiment A"}
        response = self.client.post("/batiments/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_get_all_batiments_api(self):
        response = self.client.get("/batiments/all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_search_batiments_api(self):
        response = self.client.get("/batiments/all/?search=Aile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_batiment_detail_api(self):
        response = self.client.get(f"/batiments/{self.batiment.idBatiment}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nom"], "Bâtiment A")

    def test_get_batiment_chambres_api(self):
        Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=101,
            type_chambre="INDIVIDUELLE",
            capacite=1
        )
        response = self.client.get(f"/batiments/{self.batiment.idBatiment}/chambres/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_chambres"], 1)
        self.assertEqual(len(response.data["chambres"]), 1)

    def test_update_batiment_api(self):
        payload = {"nom": "Bâtiment A Modifié", "nombre_chambre": 8}
        response = self.client.patch(f"/batiments/{self.batiment.idBatiment}/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nom"], "Bâtiment A Modifié")
        self.assertEqual(response.data["nombre_chambre"], 8)

    def test_delete_batiment_api(self):
        response = self.client.delete(f"/batiments/{self.batiment.idBatiment}/delete/")
        self.assertEqual(response.status_code, 200)
        self.batiment.refresh_from_db()
        self.assertFalse(self.batiment.actif)

        response_hard = self.client.delete(f"/batiments/{self.batiment.idBatiment}/delete/?hard=true")
        self.assertEqual(response_hard.status_code, 200)
        self.assertFalse(Batiment.objects.filter(idBatiment=self.batiment.idBatiment).exists())


