# pyrefly: ignore [missing-import]
from django.test import TestCase
# pyrefly: ignore [missing-import]
from rest_framework.test import APIClient
# pyrefly: ignore [missing-import]
from rest_framework import status
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from .models import Natalite
from .nataliteRepositories import NataliteRepository
from .nataliteServices import NataliteService


class NataliteModelAndRepositoryTests(TestCase):
    def setUp(self):
        self.user_mother = User.objects.create(
            nom="Diop",
            prenom="Fatou",
            email="fatou.diop@example.com",
            telephone="+221770001122",
            login="fatou_diop",
            motDePasseHash="hash123",
            role=User.Role.PATIENT,
        )
        self.patient_mother = Patient.objects.create(
            idUtilisateur=self.user_mother,
            dateNaissance="1995-03-15",
            sexe=Patient.Sexe.FEMININ,
            adresse="Dakar",
            groupeSanguin=Patient.GroupeSanguin.O_POSITIF,
            personneAContacter="Modou Diop",
            dateInscription="2024-01-01",
        )

        self.user_doctor = User.objects.create(
            nom="Sow",
            prenom="Awa",
            email="awa.sow@example.com",
            telephone="+221770003344",
            login="dr_awa",
            motDePasseHash="hash456",
            role=User.Role.MEDECIN,
        )
        self.medecin = Medecin.objects.create(
            idUtilisateur=self.user_doctor,
            specialite=Medecin.Specialite.GYNECOLOGIE,
            numeroOrdre="ORD-9988",
            dateEmbauche="2020-01-01",
        )

        self.repository = NataliteRepository()
        self.service = NataliteService()

    def test_create_and_query_natalite(self):
        natalite = self.repository.createNouveauNe(
            id_patient=self.patient_mother,
            id_medecin=self.medecin,
            prenom_nouveau_ne="Amina",
            nom_nouveau_ne="Diop",
            date_naissance="2024-05-10",
            sexe=Natalite.Sexe.FEMININ,
            poids=3.40,
            taille=51.0,
            lieu_naissance="Maternité Principale",
        )
        self.assertIsNotNone(natalite.id_nouveau_ne)
        self.assertEqual(str(natalite), "Amina Diop (Né(e) le 2024-05-10)")

        fetched = self.repository.get_NouveauNeById(natalite.id_nouveau_ne)
        self.assertEqual(fetched, natalite)

        by_patient = self.repository.get_nouveaux_nes_by_patient(self.patient_mother.idPatient)
        self.assertEqual(len(by_patient), 1)

        by_sexe = self.repository.get_natalities_by_sexe(Natalite.Sexe.FEMININ)
        self.assertEqual(len(by_sexe), 1)

    def test_delete_natalite_does_not_delete_all(self):
        n1 = self.repository.createNouveauNe(
            id_patient=self.patient_mother,
            date_naissance="2024-01-01",
            sexe=Natalite.Sexe.MASCULIN,
        )
        n2 = self.repository.createNouveauNe(
            id_patient=self.patient_mother,
            date_naissance="2024-02-01",
            sexe=Natalite.Sexe.FEMININ,
        )
        self.assertEqual(self.repository.get_all_nouveaux_nes().count(), 2)

        self.repository.delete_nouveau_ne(n1.id_nouveau_ne, hard=False)
        n1.refresh_from_db()
        self.assertFalse(n1.actif)

        self.repository.delete_nouveau_ne(n1.id_nouveau_ne, hard=True)
        self.assertIsNone(self.repository.get_NouveauNeById(n1.id_nouveau_ne))
        self.assertIsNotNone(self.repository.get_NouveauNeById(n2.id_nouveau_ne))



class NataliteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_mother = User.objects.create(
            nom="Traore",
            prenom="Mariam",
            email="mariam.traore@example.com",
            telephone="+22370001122",
            login="mariam_t",
            motDePasseHash="pass123",
            role=User.Role.PATIENT,
        )
        self.admin = User.objects.create(nom="Admin", prenom="Super", email="adm_nat@test.com", telephone="0101010101", login="adm_nat", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        self.client.force_authenticate(user=self.admin)
        self.patient = Patient.objects.create(
            idUtilisateur=self.user_mother,
            dateNaissance="1998-07-20",
            sexe=Patient.Sexe.FEMININ,
            adresse="Bamako",
            groupeSanguin=Patient.GroupeSanguin.B_POSITIF,
            personneAContacter="Oumar Traore",
            dateInscription="2024-01-01",
        )

    def test_api_create_and_get_natalite(self):
        payload = {
            "patient_id": self.patient.idPatient,
            "prenom_nouveau_ne": "Ibrahim",
            "nom_nouveau_ne": "Traore",
            "date_naissance": "2024-06-01",
            "sexe": "M",
            "poids": 3.65,
            "taille": 52.0,
            "lieu_naissance": "Hôpital Central",
            "observation": "En très bonne santé",
        }
        response = self.client.post("/natalite/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["prenom_nouveau_ne"], "Ibrahim")
        natality_id = response.data["id_nouveau_ne"]

        get_resp = self.client.get(f"/natalite/{natality_id}/")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data["nom_nouveau_ne"], "Traore")

    def test_api_future_date_rejected(self):
        payload = {
            "patient_id": self.patient.idPatient,
            "date_naissance": "2099-01-01",
            "sexe": "M",
        }
        response = self.client.post("/natalite/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_naissance", response.data)

    def test_natalite_soft_deleted_hidden_by_default_and_visible_with_all(self):
        """Une fiche de naissance désactivée n'apparaît pas par défaut mais réapparaît avec ?all=true."""
        nat = Natalite.objects.create(
            id_patient=self.patient, prenom_nouveau_ne="Bébé", nom_nouveau_ne="Inactif",
            date_naissance="2024-01-01", sexe="M", actif=False
        )
        # Liste par défaut -> exclu
        res_default = self.client.get("/natalite/")
        self.assertEqual(res_default.status_code, 200)
        items = res_default.data.get("results", res_default.data)
        ids = [n["id_nouveau_ne"] for n in items]
        self.assertNotIn(nat.id_nouveau_ne, ids)

        # Liste avec ?all=true -> inclus
        res_all = self.client.get("/natalite/?all=true")
        self.assertEqual(res_all.status_code, 200)
        items_all = res_all.data.get("results", res_all.data)
        ids_all = [n["id_nouveau_ne"] for n in items_all]
        self.assertIn(nat.id_nouveau_ne, ids_all)

