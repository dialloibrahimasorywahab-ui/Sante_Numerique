from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from medecin.models import Medecin
from medecin.medecinRepositories import MedecinRepository
from users.models import User


class MedecinProjectConfigTests(SimpleTestCase):
    def test_medecin_app_is_registered(self):
        self.assertTrue(apps.is_installed('medecin'))

    def test_medecin_routes_are_available(self):
        self.assertEqual(resolve('/medecins/').view_name, 'create_medecin')
        self.assertEqual(resolve('/medecins/all/').view_name, 'get_all_medecin')


class MedecinRepositoryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(nom="Admin", prenom="Super", email="adm_med@test.com", telephone="0101010101", login="adm_med", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_update_medecin_updates_fields(self):
        user = User.objects.create(
            login='dr_smith',
            motDePasseHash='hash-demo',
            role=User.Role.MEDECIN,
        )
        medecin = Medecin.objects.create(
            idUtilisateur=user,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numeroOrdre='CNOM-99999',
            telephonePro='0600000000',
            emailPro='smith@hospital.com',
            bureau='Cabinet 204',
            dateEmbauche='2020-01-15',
        )

        repository = MedecinRepository()
        updated_medecin = repository.update_Medecin(
            medecin,
            bureau='Cabinet 305',
            telephonePro='0611223344',
        )

        self.assertEqual(updated_medecin.bureau, 'Cabinet 305')
        self.assertEqual(updated_medecin.telephonePro, '0611223344')

    def test_get_non_existent_medecin_returns_none(self):
        repository = MedecinRepository()
        medecin = repository.get_medecin(9999)
        self.assertIsNone(medecin)

    def test_get_medecin_api_not_found_returns_404(self):
        response = self.client.get("/medecins/9999/")
        self.assertEqual(response.status_code, 404)

    def test_create_medecin_combined_frontend_post(self):
        payload = {
            "nom": "Camara",
            "prenom": "Aissatou",
            "email": "dr.aissatou@hospital.com",
            "telephone": "+224620000111",
            "login": "dr_aissatou_1click",
            "motDePasse": "Pass1234!",
            "specialite": "PEDIATRIE",
            "numeroOrdre": "CNOM-77777",
            "bureau": "Cabinet 302",
            "dateEmbauche": "2025-02-01",
        }
        response = self.client.post("/medecins/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Camara")
        self.assertEqual(response.data["prenom"], "Aissatou")
        self.assertEqual(response.data["specialite"], "PEDIATRIE")

    def test_get_medecins_by_service_filter(self):
        user1 = User.objects.create(login="doc_cardio", email="cardio@hospital.com", telephone="+224600000001", role=User.Role.MEDECIN)
        user2 = User.objects.create(login="doc_pedia", email="pedia@hospital.com", telephone="+224600000002", role=User.Role.MEDECIN)

        Medecin.objects.create(
            idUtilisateur=user1,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numeroOrdre="CNOM-11111",
            dateEmbauche="2025-01-01"
        )
        Medecin.objects.create(
            idUtilisateur=user2,
            specialite=Medecin.Specialite.PEDIATRIE,
            numeroOrdre="CNOM-22222",
            dateEmbauche="2025-01-01"
        )

        response = self.client.get("/medecins/service/CARDIOLOGIE/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["specialite"], "CARDIOLOGIE")

        response_param = self.client.get("/medecins/all/?service=PEDIATRIE")
        self.assertEqual(response_param.status_code, 200)
        self.assertEqual(len(response_param.data), 1)
        self.assertEqual(response_param.data[0]["specialite"], "PEDIATRIE")

    def test_update_medecin_nested_user_fields(self):
        user = User.objects.create(
            nom="Diallo", prenom="Mamadou", email="m.diallo@hosp.com",
            telephone="+224622001122", login="doc_diallo", role=User.Role.MEDECIN
        )
        medecin = Medecin.objects.create(
            idUtilisateur=user, specialite=Medecin.Specialite.NEUROLOGIE,
            numeroOrdre="CNOM-33333", dateEmbauche="2025-01-01", bureau="Cabinet 1"
        )
        update_payload = {
            "nom": "Diallo-Bah",
            "bureau": "Cabinet 5",
        }
        response = self.client.patch(f"/medecins/{medecin.idMedecin}/update/", update_payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nom"], "Diallo-Bah")
        self.assertEqual(response.data["bureau"], "Cabinet 5")
        user.refresh_from_db()
        self.assertEqual(user.nom, "Diallo-Bah")

