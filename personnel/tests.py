from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from personnel.models import Personnel
from personnel.personnelRepositories import PersonnelRepository
from users.models import User


class PersonnelProjectConfigTests(SimpleTestCase):
    def test_personnel_app_is_registered(self):
        self.assertTrue(apps.is_installed('personnel'))

    def test_personnel_routes_are_available(self):
        self.assertEqual(resolve('/personnel/').view_name, 'create_personnel')
        self.assertEqual(resolve('/personnel/all/').view_name, 'get_all_personnel')


class PersonnelRepositoryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(nom="Admin", prenom="Super", email="adm_pers@test.com", telephone="0101010101", login="adm_pers", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_update_personnel_updates_fields(self):
        user = User.objects.create(
            login='inf_nurse',
            email='inf@hospital.com',
            telephone='+224600112233',
            role=User.Role.INFIRMIER,
        )
        personnel = Personnel.objects.create(
            idUtilisateur=user,
            typePersonnel=Personnel.TypePersonnel.INFIRMIER,
            poste='Infirmière de Garde',
            serviceHopital='Urgences',
            dateEmbauche='2024-01-10',
        )

        repository = PersonnelRepository()
        updated_personnel = repository.update_Personnel(
            personnel,
            poste='Infirmière Chef',
            serviceHopital='Réanimation',
        )

        self.assertEqual(updated_personnel.poste, 'Infirmière Chef')
        self.assertEqual(updated_personnel.serviceHopital, 'Réanimation')

    def test_get_non_existent_personnel_returns_none(self):
        repository = PersonnelRepository()
        personnel = repository.get_personnel(9999)
        self.assertIsNone(personnel)

    def test_get_personnel_api_not_found_returns_404(self):
        response = self.client.get("/personnel/9999/")
        self.assertEqual(response.status_code, 404)

    def test_create_personnel_combined_frontend_post(self):
        payload = {
            "nom": "Bah",
            "prenom": "Mariama",
            "email": "mariama.bah@hospital.com",
            "telephone": "+224621998877",
            "dateNaissance": "1992-04-15",
            "login": "mariama_inf_1click",
            "motDePasse": "InfPass123!",
            "typePersonnel": "INFIRMIER",
            "poste": "Infirmière Soignante",
            "serviceHopital": "Pédiatrie",
            "matricule": "EMP-INF-999",
            "dateEmbauche": "2024-03-01",
        }
        response = self.client.post("/personnel/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Bah")
        self.assertEqual(response.data["prenom"], "Mariama")
        self.assertEqual(response.data["typePersonnel"], "INFIRMIER")

    def test_update_personnel_nested_user_fields(self):
        user = User.objects.create(
            nom="Camara", prenom="Aminata", email="a.camara@hosp.com",
            telephone="+224623112233", login="inf_aminata", role=User.Role.INFIRMIER
        )
        personnel = Personnel.objects.create(
            idUtilisateur=user, typePersonnel=Personnel.TypePersonnel.INFIRMIER,
            poste="Infirmière", serviceHopital="Urgences", dateEmbauche="2024-01-01"
        )
        update_payload = {
            "prenom": "Aminata Binta",
            "poste": "Infirmière Major",
        }
        response = self.client.patch(f"/personnel/{personnel.idPersonnel}/update/", update_payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["prenom"], "Aminata Binta")
        self.assertEqual(response.data["poste"], "Infirmière Major")
        user.refresh_from_db()
        self.assertEqual(user.prenom, "Aminata Binta")

    def test_create_personnel_empty_payload_returns_400(self):
        response = self.client.post("/personnel/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("nom", response.data)
        self.assertIn("prenom", response.data)
        self.assertIn("login", response.data)


