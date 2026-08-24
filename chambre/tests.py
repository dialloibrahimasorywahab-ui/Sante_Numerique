from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from .models import Chambre
from .chambreRepositories import ChambreRepository
from .chambreServices import ChambreService
from batiment.models import Batiment


class ChambreConfigTests(SimpleTestCase):
    def test_chambre_app_is_installed(self):
        self.assertTrue(apps.is_installed('chambre'))

    def test_chambre_routes_are_available(self):
        self.assertEqual(resolve('/chambres/').view_name, 'create_chambre')
        self.assertEqual(resolve('/chambres/all/').view_name, 'get_all_chambres')


class ChambreModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.repository = ChambreRepository()
        self.service = ChambreService()
        self.batiment = Batiment.objects.create(nom="Bâtiment Test A", nombre_chambre=0)

    def test_create_and_get_chambre(self):
        chambre = self.repository.create_chambre(
            batiment=self.batiment,
            numero_chambre=101,
            type_chambre=Chambre.TypeChambre.INDIVIDUELLE,
            capacite=1
        )
        self.assertIsNotNone(chambre.id)
        self.assertEqual(chambre.idChambre, chambre.id)
        self.assertEqual(chambre.capacite, 1)

        fetched = self.repository.get_chambre(chambre.id)
        self.assertEqual(fetched, chambre)

    def test_get_chambres_by_batiment_and_search(self):
        chambre1 = self.repository.create_chambre(batiment=self.batiment, numero_chambre=101, capacite=1)
        chambre2 = self.repository.create_chambre(batiment=self.batiment, numero_chambre=102, capacite=2)

        by_bat = self.repository.get_chambres_by_batiment(self.batiment.idBatiment)
        self.assertEqual(len(by_bat), 2)

        searched = self.repository.search_chambres("102")
        self.assertEqual(len(searched), 1)
        self.assertEqual(searched[0].numero_chambre, 102)


class ChambreAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.batiment = Batiment.objects.create(nom="Pavillon A", nombre_chambre=0)
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=101,
            type_chambre="INDIVIDUELLE",
            capacite=1
        )

    def test_create_chambre_api_with_id_batiment(self):
        payload = {
            "id_batiment": self.batiment.idBatiment,
            "numero_chambre": 102,
            "type_chambre": "DOUBLE",
            "capacite": 2
        }
        response = self.client.post("/chambres/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["numero_chambre"], 102)
        self.assertEqual(response.data["capacite"], 2)

    def test_get_all_chambres_api(self):
        response = self.client.get("/chambres/all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.chambre.id)

    def test_get_chambre_detail_api(self):
        response = self.client.get(f"/chambres/{self.chambre.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["numero_chambre"], 101)

    def test_update_chambre_api(self):
        payload = {"capacite": 3}
        response = self.client.patch(f"/chambres/{self.chambre.id}/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["capacite"], 3)

    def test_get_chambres_by_type_api(self):
        Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=103,
            type_chambre="COMMUNE",
            capacite=4
        )
        response = self.client.get("/chambres/all/?type_chambre=COMMUNE")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type_chambre"], "COMMUNE")

        response_route = self.client.get("/chambres/type/COMMUNE/")
        self.assertEqual(response_route.status_code, 200)
        self.assertEqual(len(response_route.data), 1)

    def test_get_chambres_by_statut_api(self):
        response = self.client.get("/chambres/all/?statut=DISPONIBLE")
        self.assertEqual(response.status_code, 200)

        response_route = self.client.get("/chambres/statut/DISPONIBLE/")
        self.assertEqual(response_route.status_code, 200)

    def test_delete_chambre_api(self):
        response = self.client.delete(f"/chambres/{self.chambre.id}/delete/")
        self.assertEqual(response.status_code, 200)
        self.chambre.refresh_from_db()
        self.assertEqual(self.chambre.statut, "HORS_SERVICE")

        response_hard = self.client.delete(f"/chambres/{self.chambre.id}/delete/?hard=true")
        self.assertEqual(response_hard.status_code, 200)
        self.assertFalse(Chambre.objects.filter(id=self.chambre.id).exists())



