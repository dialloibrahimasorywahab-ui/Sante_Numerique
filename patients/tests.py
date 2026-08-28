from django.apps import apps
from django.test import SimpleTestCase, TestCase
from django.urls import resolve
from rest_framework.test import APIClient

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


class PatientAPIPermissionsAndCreationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create(
            nom="Admin", prenom="Super", email="admin.test@hospital.com",
            telephone="+224620000001", login="admin_test", motDePasseHash="hash",
            role=User.Role.ADMINISTRATEUR
        )
        self.medecin = User.objects.create(
            nom="Diallo", prenom="Mamadou", email="dr.diallo@hospital.com",
            telephone="+224620000002", login="dr_diallo", motDePasseHash="hash",
            role=User.Role.MEDECIN
        )
        self.infirmier = User.objects.create(
            nom="Barry", prenom="Aissatou", email="inf.barry@hospital.com",
            telephone="+224620000003", login="inf_barry", motDePasseHash="hash",
            role=User.Role.INFIRMIER
        )
        self.user_patient = User.objects.create(
            nom="Sow", prenom="Alpha", email="patient.sow@example.com",
            telephone="+224620000004", login="patient_sow", motDePasseHash="hash",
            role=User.Role.PATIENT
        )
        self.patient_record = Patient.objects.create(
            idUtilisateur=self.user_patient,
            dateNaissance="1992-06-15",
            sexe=Patient.Sexe.MASCULIN,
            adresse="Dixinn, Conakry",
            groupeSanguin=Patient.GroupeSanguin.O_POSITIF,
            numeroSecuriteSociale="1920615000111",
            personneAContacter="Mariama Sow",
            dateInscription="2024-01-10"
        )

        self.valid_patient_payload = {
            "nom": "Kaba",
            "prenom": "Sekou",
            "email": "sekou.kaba@example.com",
            "telephone": "+224622334455",
            "login": "sekou_patient",
            "motDePasse": "PatientPass123!",
            "dateNaissance": "1995-05-12",
            "sexe": "M",
            "adresse": "Kaloum, Conakry",
            "groupeSanguin": "O+",
            "numeroSecuriteSociale": "1950512999888",
            "personneAContacter": "Moussa Kaba",
        }

    def test_infirmier_cannot_create_patient_returns_403(self):
        """Un infirmier connecté ne peut pas créer de patient (403 et aucun enregistrement en BD)."""
        self.client.force_authenticate(user=self.infirmier)
        initial_patient_count = Patient.objects.count()
        initial_user_count = User.objects.count()

        response = self.client.post("/patients/", self.valid_patient_payload, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.data)
        self.assertIn("Seul un médecin ou un administrateur", response.data["error"])
        self.assertEqual(Patient.objects.count(), initial_patient_count)
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertFalse(User.objects.filter(login="sekou_patient").exists())

    def test_patient_cannot_create_patient_returns_403(self):
        """Un patient connecté ne peut pas créer de patient (403 et aucun enregistrement en BD)."""
        self.client.force_authenticate(user=self.user_patient)
        initial_patient_count = Patient.objects.count()
        initial_user_count = User.objects.count()

        response = self.client.post("/patients/", self.valid_patient_payload, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Patient.objects.count(), initial_patient_count)
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertFalse(User.objects.filter(login="sekou_patient").exists())

    def test_unauthenticated_cannot_create_patient_returns_401(self):
        """Un utilisateur non authentifié ne peut pas créer de patient (401)."""
        self.client.logout()
        response = self.client.post("/patients/", self.valid_patient_payload, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertFalse(User.objects.filter(login="sekou_patient").exists())

    def test_medecin_can_create_patient_success(self):
        """Un médecin peut créer un dossier patient combiné avec succès (201)."""
        self.client.force_authenticate(user=self.medecin)

        response = self.client.post("/patients/", self.valid_patient_payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Kaba")
        self.assertEqual(response.data["prenom"], "Sekou")
        self.assertEqual(response.data["email"], "sekou.kaba@example.com")
        self.assertEqual(response.data["groupeSanguin"], "O+")

        # Vérification en base de données
        patient = Patient.objects.get(idPatient=response.data["idPatient"])
        self.assertEqual(patient.idUtilisateur.login, "sekou_patient")
        self.assertEqual(patient.idUtilisateur.role, User.Role.PATIENT)
        self.assertTrue(patient.idUtilisateur.check_password("PatientPass123!"))

    def test_admin_can_create_patient_success(self):
        """Un administrateur peut créer un dossier patient avec succès (201)."""
        self.client.force_authenticate(user=self.admin)
        payload = self.valid_patient_payload.copy()
        payload["login"] = "admin_created_patient"
        payload["email"] = "patient.admin@example.com"
        payload["telephone"] = "+224622114477"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Kaba")
        self.assertTrue(Patient.objects.filter(idUtilisateur__login="admin_created_patient").exists())

    def test_create_patient_with_existing_user_id(self):
        """Création d'un dossier patient lié à un compte utilisateur PATIENT déjà existant."""
        self.client.force_authenticate(user=self.medecin)
        existing_user = User.objects.create(
            nom="Camara", prenom="Abou", email="abou.camara@example.com",
            telephone="+224622887766", login="abou_camara", motDePasseHash="hash",
            role=User.Role.PATIENT
        )
        payload = {
            "idUtilisateur": existing_user.idUser,
            "dateNaissance": "1998-03-22",
            "sexe": "M",
            "adresse": "Matam, Conakry",
            "groupeSanguin": "B+",
            "numeroSecuriteSociale": "1980322555666",
            "personneAContacter": "Fode Camara",
        }

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nom"], "Camara")
        self.assertEqual(response.data["groupeSanguin"], "B+")
        self.assertEqual(response.data["idUtilisateur"], existing_user.idUser)

    def test_create_patient_missing_required_fields_returns_400(self):
        """Validation : erreur 400 si les champs obligatoires du compte sont manquants."""
        self.client.force_authenticate(user=self.medecin)
        payload = {
            "nom": "SeulNom",
            "adresse": "Conakry",
        }

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("prenom", response.data)
        self.assertIn("login", response.data)

    def test_create_patient_invalid_telephone_returns_400(self):
        """Validation : erreur 400 pour un numéro de téléphone invalide."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["telephone"] = "invalide_phone_123"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("telephone", response.data)

    def test_create_patient_future_date_naissance_returns_400(self):
        """Validation : erreur 400 pour une date de naissance dans le futur."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["dateNaissance"] = "2099-01-01"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("dateNaissance", response.data)

    def test_create_patient_invalid_blood_group_returns_400(self):
        """Validation : erreur 400 pour un groupe sanguin inexistant."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["groupeSanguin"] = "Z+"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("groupeSanguin", response.data)

    def test_create_patient_duplicate_login_returns_400(self):
        """Intégrité : erreur 400 lors de la tentative de création avec un login ou email déjà utilisé."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["login"] = self.user_patient.login  # login déjà existant

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_patient_cannot_list_patients_returns_403(self):
        """Un patient ne peut pas accéder à la liste de tous les patients (403)."""
        self.client.force_authenticate(user=self.user_patient)

        response_list = self.client.get("/patients/")
        self.assertEqual(response_list.status_code, 403)

        response_all = self.client.get("/patients/all/")
        self.assertEqual(response_all.status_code, 403)

    def test_infirmier_can_list_and_search_patients(self):
        """Un infirmier peut consulter la liste des patients (200)."""
        self.client.force_authenticate(user=self.infirmier)

        response = self.client.get("/patients/")
        self.assertEqual(response.status_code, 200)

        response_search = self.client.get("/patients/?search=Sow")
        self.assertEqual(response_search.status_code, 200)

    def test_patient_can_view_only_own_profile(self):
        """Un patient peut consulter uniquement son propre dossier (IsOwnerOrStaff)."""
        other_user = User.objects.create(
            nom="Autre", prenom="Patient", email="autre@example.com",
            telephone="+224622000099", login="autre_pat", motDePasseHash="hash",
            role=User.Role.PATIENT
        )
        other_patient = Patient.objects.create(
            idUtilisateur=other_user,
            dateNaissance="1985-01-01",
            sexe=Patient.Sexe.FEMININ,
            adresse="Ratoma",
            groupeSanguin=Patient.GroupeSanguin.A_POSITIF,
            personneAContacter="Test",
            dateInscription="2024-01-01"
        )

        self.client.force_authenticate(user=self.user_patient)

        # Accès à son propre dossier -> 200 OK
        res_own = self.client.get(f"/patients/{self.patient_record.idPatient}/")
        self.assertEqual(res_own.status_code, 200)
        self.assertEqual(res_own.data["idPatient"], self.patient_record.idPatient)

        # Accès au dossier d'un autre patient -> 403 Forbidden
        res_other = self.client.get(f"/patients/{other_patient.idPatient}/")
        self.assertEqual(res_other.status_code, 403)

    def test_patient_and_infirmier_cannot_delete_patient(self):
        """Ni le patient ni l'infirmier ne peuvent supprimer un dossier patient (réservé admin)."""
        # Patient -> 403 Forbidden
        self.client.force_authenticate(user=self.user_patient)
        res_pat = self.client.delete(f"/patients/{self.patient_record.idPatient}/")
        self.assertEqual(res_pat.status_code, 403)

        # Infirmier -> 403 Forbidden
        self.client.force_authenticate(user=self.infirmier)
        res_inf = self.client.delete(f"/patients/{self.patient_record.idPatient}/")
        self.assertEqual(res_inf.status_code, 403)
