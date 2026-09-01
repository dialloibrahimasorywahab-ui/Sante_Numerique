from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from .models import Mortalite
from .mortaliteRepositories import MortaliteRepository


class MortaliteModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            nom="Diallo",
            prenom="Amadou",
            email="amadou.diallo@example.com",
            telephone="+224600001122",
            login="amadou_d",
            motDePasseHash="pass123",
            role=User.Role.PATIENT,
        )
        self.patient = Patient.objects.create(
            idUtilisateur=self.user,
            dateNaissance="1950-01-01",
            sexe=Patient.Sexe.MASCULIN,
            adresse="Conakry",
            groupeSanguin=Patient.GroupeSanguin.A_POSITIF,
            personneAContacter="Mamadou Diallo",
            dateInscription="2024-01-01",
        )

        self.repository = MortaliteRepository()

    def test_create_mortalite(self):
        deces = self.repository.createDeces(
            id_patient=self.patient,
            date_deces="2024-04-15",
            cause_deces="Arrêt cardiaque",
            lieu_deces="Service Urgences",
        )
        self.assertIsNotNone(deces.id_deces)
        self.assertIn("Amadou Diallo", str(deces))

        fetched = self.repository.get_DecesById(deces.id_deces)
        self.assertEqual(fetched, deces)


class MortaliteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            nom="Camara",
            prenom="Fanta",
            email="fanta.camara@example.com",
            telephone="+224600003344",
            login="fanta_c",
            motDePasseHash="pass123",
            role=User.Role.PATIENT,
        )
        self.admin = User.objects.create(nom="Admin", prenom="Super", email="adm_mor@test.com", telephone="0101010101", login="adm_mor", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        self.client.force_authenticate(user=self.admin)
        self.patient = Patient.objects.create(
            idUtilisateur=self.user,
            dateNaissance="1965-06-10",
            sexe=Patient.Sexe.FEMININ,
            adresse="Kindia",
            groupeSanguin=Patient.GroupeSanguin.O_NEGATIF,
            personneAContacter="Sory Camara",
            dateInscription="2024-01-01",
        )

    def test_api_create_and_get_mortalite(self):
        payload = {
            "patient_id": self.patient.idPatient,
            "date_deces": "2024-05-20",
            "cause_deces": "Insuffisance respiratoire aiguë",
            "lieu_deces": "Hôpital Ignace Deen",
        }
        response = self.client.post("/mortalite/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cause_deces"], "Insuffisance respiratoire aiguë")

        deces_id = response.data["id_deces"]
        get_resp = self.client.get(f"/mortalite/{deces_id}/")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)

    def test_mortalite_soft_deleted_hidden_by_default_and_visible_with_all(self):
        """Une fiche de décès désactivée n'apparaît pas par défaut mais réapparaît avec ?all=true."""
        dec = Mortalite.objects.create(
            id_patient=self.patient, date_deces="2024-01-01", cause_deces="Test",
            lieu_deces="Test lieu", actif=False
        )
        # Liste par défaut -> exclu
        res_default = self.client.get("/mortalite/")
        self.assertEqual(res_default.status_code, 200)
        items = res_default.data.get("results", res_default.data)
        ids = [m["id_deces"] for m in items]
        self.assertNotIn(dec.id_deces, ids)

        # Liste avec ?all=true -> inclus
        res_all = self.client.get("/mortalite/?all=true")
        self.assertEqual(res_all.status_code, 200)
        items_all = res_all.data.get("results", res_all.data)
        ids_all = [m["id_deces"] for m in items_all]
        self.assertIn(dec.id_deces, ids_all)

