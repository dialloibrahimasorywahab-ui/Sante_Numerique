from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve

from patients.models import Patient
from patients.patientRepositories import PatientRepository
from users.models import User


class PatientsProjectConfigTests(SimpleTestCase):
    def test_patients_app_is_registered(self):
        self.assertTrue(apps.is_installed('patients'))

    def test_patient_routes_are_available(self):
        self.assertEqual(resolve('/patients/').view_name, 'create_patient')
        self.assertEqual(resolve('/patients/all/').view_name, 'get_all_patient')


class PatientRepositoryTests(TestCase):
    def test_update_patient_updates_fields(self):
        user = User.objects.create(
            login='alice',
            motDePasseHash='hash-demo',
            role=User.Role.PATIENT,
        )
        patient = Patient.objects.create(
            idUtilisateur=user,
            dateNaissance='1990-01-20',
            sexe=Patient.Sexe.FEMININ,
            adresse='12 rue de la Paix',
            groupeSanguin=Patient.GroupeSanguin.A_POSITIF,
            numeroSecuriteSociale='1234567890123',
            personneAContacter='Jean Dupont',
            dateInscription='2024-01-05',
        )

        repository = PatientRepository()
        updated_patient = repository.update_Patient(
            patient,
            adresse='15 Avenue des Champs',
            personneAContacter='Marie Dupont',
        )

        self.assertEqual(updated_patient.adresse, '15 Avenue des Champs')
        self.assertEqual(updated_patient.personneAContacter, 'Marie Dupont')

    def test_get_non_existent_patient_returns_none(self):
        repository = PatientRepository()
        patient = repository.get_patient(9999)
        self.assertIsNone(patient)

    def test_get_patient_api_not_found_returns_404(self):
        from rest_framework.test import APIClient
        admin = User.objects.create(nom="Admin", prenom="Super", email="adm_pat@test.com", telephone="0101010101", login="adm_pat", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.get("/patients/9999/")
        self.assertEqual(response.status_code, 404)

    def test_create_patient_combined_frontend_post(self):
        from rest_framework.test import APIClient
        admin = User.objects.create(nom="Admin", prenom="Super", email="adm_pat2@test.com", telephone="0101010102", login="adm_pat2", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        client = APIClient()
        client.force_authenticate(user=admin)
        payload = {
            "nom": "Kaba",
            "prenom": "Sekou",
            "email": "sekou.kaba@example.com",
            "telephone": "+224622334455",
            "login": "sekou_patient",
            "motDePasse": "PatientPass123!",
            "dateNaissance": "1995-05-12",
            "sexe": "M",
            "adresse": "Kaloum Conakry",
            "groupeSanguin": "O+",
            "numeroSecuriteSociale": "1950512999888",
            "personneAContacter": "Moussa Kaba",
        }
        response = client.post("/patients/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Kaba")
        self.assertEqual(response.data["prenom"], "Sekou")
        self.assertEqual(response.data["groupeSanguin"], "O+")

