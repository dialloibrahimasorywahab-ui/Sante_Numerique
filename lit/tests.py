# pyrefly: ignore [missing-import]
from django.apps import apps
# pyrefly: ignore [missing-import]
from django.test import SimpleTestCase, TestCase
# pyrefly: ignore [missing-import]
from django.urls import resolve
# pyrefly: ignore [missing-import]
from rest_framework.test import APIClient

from .models import Lit
from .litRepositories import LitRepository
from .litServices import LitService
from batiment.models import Batiment
from chambre.models import Chambre


class LitConfigTests(SimpleTestCase):
    def test_lit_app_is_installed(self):
        self.assertTrue(apps.is_installed('lit'))

    def test_lit_routes_are_available(self):
        self.assertEqual(resolve('/lits/').view_name, 'create_lit')
        self.assertEqual(resolve('/lits/all/').view_name, 'get_all_lits')


class LitModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.repository = LitRepository()
        self.service = LitService()
        self.batiment = Batiment.objects.create(nom="Bâtiment Test B", nombre_chambre=1)
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=201,
            type_chambre=Chambre.TypeChambre.DOUBLE,
            capacite=2
        )

    def test_create_and_get_lit(self):
        lit = self.repository.create_lit(
            chambre=self.chambre,
            numero_lit="Lit 1",
            etat=Lit.EtatLit.DISPONIBLE
        )
        self.assertIsNotNone(lit.id)
        self.assertEqual(lit.idLit, lit.id)
        self.assertEqual(lit.etat, Lit.EtatLit.DISPONIBLE)

        fetched = self.repository.get_lit(lit.id)
        self.assertEqual(fetched, lit)

    def test_generate_lits_pour_chambre(self):
        lits_crees = self.service.generate_lits_pour_chambre(self.chambre)
        self.assertEqual(len(lits_crees), 2)
        self.assertEqual(self.chambre.lits.count(), 2)

    def test_filter_by_etat_and_search(self):
        self.repository.create_lit(chambre=self.chambre, numero_lit="Lit A", etat=Lit.EtatLit.DISPONIBLE)
        self.repository.create_lit(chambre=self.chambre, numero_lit="Lit B", etat=Lit.EtatLit.OCCUPE)

        dispo = self.repository.get_lits_by_etat(Lit.EtatLit.DISPONIBLE)
        self.assertEqual(len(dispo), 1)

        searched = self.repository.search_lits("Lit B")
        self.assertEqual(len(searched), 1)


class LitAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.batiment = Batiment.objects.create(nom="Bâtiment API", nombre_chambre=1)
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=301,
            type_chambre="DOUBLE",
            capacite=2

        )
        self.lit = Lit.objects.create(
            chambre=self.chambre,
            numero_lit="Lit #1",
            etat="DISPONIBLE"
        )

    def test_create_lit_api(self):
        payload = {
            "id_chambre": self.chambre.id,
            "numero_lit": "Lit #2",
            "etat": "DISPONIBLE"
        }
        response = self.client.post("/lits/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["numero_lit"], "Lit #2")

    def test_get_all_lits_api(self):
        response = self.client.get("/lits/all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_lit_detail_api(self):
        response = self.client.get(f"/lits/{self.lit.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["numero_lit"], "Lit #1")

    def test_update_lit_api(self):
        payload = {"etat": "OCCUPE"}
        response = self.client.patch(f"/lits/{self.lit.id}/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["etat"], "OCCUPE")

    def test_delete_lit_api(self):
        response = self.client.delete(f"/lits/{self.lit.id}/delete/")
        self.assertEqual(response.status_code, 200)
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.etat, "HORS_SERVICE")

        response_hard = self.client.delete(f"/lits/{self.lit.id}/delete/?hard=true")
        self.assertEqual(response_hard.status_code, 200)
        self.assertFalse(Lit.objects.filter(id=self.lit.id).exists())

