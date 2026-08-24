# pyrefly: ignore [missing-import]
from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from .models import RendezVous
from .rendezvousRepositories import RendezVousRepository
from .rendezvousServices import RendezVousService
from users.models import User
from patients.models import Patient
from medecin.models import Medecin


class RendezvousConfigTests(SimpleTestCase):
    def test_rendezvous_app_is_installed(self):
        self.assertTrue(apps.is_installed('rendezvous'))

    def test_rendezvous_routes_are_available(self):
        self.assertEqual(resolve('/rendezvous/').view_name, 'create_rendezvous')
        self.assertEqual(resolve('/rendezvous/all/').view_name, 'get_all_rendezvous')
        self.assertEqual(resolve('/rdv/all/').view_name, 'get_all_rendezvous')


class RendezVousModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.repository = RendezVousRepository()
        self.service = RendezVousService()

        user_pat = User.objects.create(nom="KOUASSI", prenom="Awa", email="pat_repo@test.com", telephone="0101010101", login="pat_user_repo", motDePasseHash="hash", role=User.Role.PATIENT)
        self.patient = Patient.objects.create(idUtilisateur=user_pat, sexe="F", adresse="Abidjan", groupeSanguin="O+", numeroSecuriteSociale="12345", personneAContacter="Mom", dateInscription="2026-01-01")

        user_med = User.objects.create(nom="TRAORE", prenom="Ibrahim", email="med_repo@test.com", telephone="0202020202", login="med_user_repo", motDePasseHash="hash", role=User.Role.MEDECIN)
        self.medecin = Medecin.objects.create(idUtilisateur=user_med, specialite="CARDIOLOGIE", matricule="MED100", numeroOrdre="ORD100", dateEmbauche="2020-01-01")



    def test_create_and_get_rendezvous(self):
        rdv = self.repository.create_rendezvous(
            patient=self.patient,
            medecin=self.medecin,
            date_rdv="2026-09-01",
            heure="10:30:00",
            motif="Consultation annuelle",
            statut=RendezVous.StatutRendezVous.PROGRAMME
        )
        self.assertIsNotNone(rdv.id)
        self.assertEqual(rdv.idRendezVous, rdv.id)
        self.assertEqual(rdv.statut, "PROGRAMME")

        fetched = self.repository.get_rendezvous(rdv.id)
        self.assertEqual(fetched, rdv)

    def test_get_by_patient_medecin_and_statut(self):
        rdv = self.repository.create_rendezvous(
            patient=self.patient,
            medecin=self.medecin,
            date_rdv="2026-09-01",
            heure="14:00:00",
            motif="Suivi ECG",
            statut=RendezVous.StatutRendezVous.CONFIRME
        )

        by_pat = self.repository.get_rendezvous_by_patient(self.patient.idPatient)
        self.assertEqual(len(by_pat), 1)

        by_med = self.repository.get_rendezvous_by_medecin(self.medecin.idMedecin)
        self.assertEqual(len(by_med), 1)

        by_statut = self.repository.get_rendezvous_by_statut("CONFIRME")
        self.assertEqual(len(by_statut), 1)


class RendezVousAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        user_pat = User.objects.create(nom="KOUASSI", prenom="Awa", email="pat_api@test.com", telephone="0303030303", login="pat_user_api", motDePasseHash="hash", role=User.Role.PATIENT)
        self.patient = Patient.objects.create(idUtilisateur=user_pat, sexe="F", adresse="Abidjan", groupeSanguin="O+", numeroSecuriteSociale="12345", personneAContacter="Mom", dateInscription="2026-01-01")

        user_med = User.objects.create(nom="TRAORE", prenom="Ibrahim", email="med_api@test.com", telephone="0404040404", login="med_user_api", motDePasseHash="hash", role=User.Role.MEDECIN)
        self.medecin = Medecin.objects.create(idUtilisateur=user_med, specialite="CARDIOLOGIE", matricule="MED101", numeroOrdre="ORD101", dateEmbauche="2020-01-01")



        self.rdv = RendezVous.objects.create(
            patient=self.patient,
            medecin=self.medecin,
            date_rdv="2026-09-10",
            heure="09:00:00",
            motif="Bilan général",
            statut="PROGRAMME"
        )

    def test_create_rendezvous_api(self):
        payload = {
            "id_patient": self.patient.idPatient,
            "id_medecin": self.medecin.idMedecin,
            "date_rdv": "2026-09-15",
            "heure": "11:00:00",
            "motif": "Contrôle tension",
            "statut": "PROGRAMME"
        }
        response = self.client.post("/rendezvous/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["motif"], "Contrôle tension")

    def test_get_all_rendezvous_api(self):
        response = self.client.get("/rendezvous/all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_rendezvous_by_statut_api(self):
        response = self.client.get("/rendezvous/statut/PROGRAMME/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_update_rendezvous_api(self):
        payload = {"statut": "CONFIRME"}
        response = self.client.patch(f"/rendezvous/{self.rdv.id}/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["statut"], "CONFIRME")

    def test_delete_rendezvous_api(self):
        response = self.client.delete(f"/rendezvous/{self.rdv.id}/delete/")
        self.assertEqual(response.status_code, 200)
        self.rdv.refresh_from_db()
        self.assertEqual(self.rdv.statut, "ANNULE")

        response_hard = self.client.delete(f"/rendezvous/{self.rdv.id}/delete/?hard=true")
        self.assertEqual(response_hard.status_code, 200)
        self.assertFalse(RendezVous.objects.filter(id=self.rdv.id).exists())

