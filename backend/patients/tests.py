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


class PatientRepositoryTests(TestCase):
    def test_update_patient_updates_fields(self):
        user = User.objects.create(
            login='alice',
            motDePasseHash='hash-demo',
            role=User.Role.PATIENT,
        )
        patient = Patient.objects.create(
            id_utilisateur=user,
            date_naissance='1990-01-20',
            sexe=Patient.Sexe.FEMININ,
            adresse='12 rue de la Paix',
            groupe_sanguin=Patient.GroupeSanguin.A_POSITIF,
            numero_securite_sociale='1234567890123',
            personne_a_contacter='Jean Dupont',
            date_inscription='2024-01-05',
        )

        repository = PatientRepository()
        updated_patient = repository.update_Patient(
            patient,
            adresse='15 Avenue des Champs',
            personne_a_contacter='Marie Dupont',
        )

        self.assertEqual(updated_patient.adresse, '15 Avenue des Champs')
        self.assertEqual(updated_patient.personne_a_contacter, 'Marie Dupont')

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
            id_utilisateur=self.user_patient,
            date_naissance="1992-06-15",
            sexe=Patient.Sexe.MASCULIN,
            adresse="Dixinn, Conakry",
            groupe_sanguin=Patient.GroupeSanguin.O_POSITIF,
            numero_securite_sociale="1920615000111",
            personne_a_contacter="Mariama Sow",
            date_inscription="2024-01-10"
        )

        self.valid_patient_payload = {
            "nom": "Kaba",
            "prenom": "Sekou",
            "email": "sekou.kaba@example.com",
            "telephone": "+224622334455",
            "login": "sekou_patient",
            "motDePasse": "TestSecurise2026!",
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
        data = response.json()
        self.assertEqual(data["nom"], "Kaba")
        self.assertEqual(data["prenom"], "Sekou")
        self.assertEqual(data["email"], "sekou.kaba@example.com")
        self.assertEqual(data["groupeSanguin"], "O+")

        # Vérification en base de données
        patient = Patient.objects.get(pk=data["idPatient"])
        self.assertEqual(patient.id_utilisateur.login, "sekou_patient")
        self.assertEqual(patient.id_utilisateur.role, User.Role.PATIENT)
        self.assertTrue(patient.id_utilisateur.check_password("TestSecurise2026!"))

    def test_medecin_can_create_patient_with_auto_credentials(self):
        """Un médecin peut créer un patient sans spécifier manuellement login ni mot de passe."""
        self.client.force_authenticate(user=self.medecin)
        payload = {
            "nom": "Traore",
            "prenom": "Fatou",
            "email": "fatou.traore@example.com",
            "telephone": "+224622998877",
            "dateNaissance": "1998-03-22",
            "sexe": "F",
            "groupeSanguin": "A+",
            "adresse": "Matam, Conakry",
        }
        response = self.client.post("/patients/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nom"], "Traore")
        self.assertEqual(data["prenom"], "Fatou")
        patient = Patient.objects.get(pk=data["idPatient"])
        self.assertEqual(patient.id_utilisateur.login, "fatou.traore")
        self.assertEqual(patient.id_utilisateur.role, User.Role.PATIENT)
        self.assertTrue(patient.id_utilisateur.has_usable_password())
        self.assertFalse(patient.id_utilisateur.check_password("PatientPass123!"))

    def test_create_patient_weak_password_returns_400(self):
        """Validation : erreur 400 si un mot de passe trop simple/court est fourni."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["login"] = "new_weak_test"
        payload["email"] = "weak@example.com"
        payload["telephone"] = "+224622001199"
        payload["motDePasse"] = "123"
        response = self.client.post("/patients/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("mot_de_passe", response.data)


    def test_admin_can_create_patient_success(self):
        """Un administrateur peut créer un dossier patient avec succès (201)."""
        self.client.force_authenticate(user=self.admin)
        payload = self.valid_patient_payload.copy()
        payload["login"] = "admin_created_patient"
        payload["email"] = "patient.admin@example.com"
        payload["telephone"] = "+224622114477"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nom"], "Kaba")
        self.assertTrue(Patient.objects.filter(id_utilisateur__login="admin_created_patient").exists())

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
        data = response.json()
        self.assertEqual(data["nom"], "Camara")
        self.assertEqual(data["groupeSanguin"], "B+")
        self.assertEqual(data["idUtilisateur"], existing_user.idUser)

    def test_create_patient_missing_required_fields_returns_400(self):
        """Validation : erreur 400 si les champs obligatoires du compte sont manquants."""
        self.client.force_authenticate(user=self.medecin)
        payload = {
            "nom": "SeulNom",
            "adresse": "Conakry",
        }

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("prenom", data)
        self.assertIn("login", data)

    def test_create_patient_invalid_telephone_returns_400(self):
        """Validation : erreur 400 pour un numéro de téléphone invalide."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["telephone"] = "invalide_phone_123"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("telephone", data)

    def test_create_patient_future_date_naissance_returns_400(self):
        """Validation : erreur 400 pour une date de naissance dans le futur."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["dateNaissance"] = "2099-01-01"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("dateNaissance", data)

    def test_create_patient_invalid_blood_group_returns_400(self):
        """Validation : erreur 400 pour un groupe sanguin inexistant."""
        self.client.force_authenticate(user=self.medecin)
        payload = self.valid_patient_payload.copy()
        payload["groupeSanguin"] = "Z+"

        response = self.client.post("/patients/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("groupeSanguin", data)

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
            id_utilisateur=other_user,
            date_naissance="1985-01-01",
            sexe=Patient.Sexe.FEMININ,
            adresse="Ratoma",
            groupe_sanguin=Patient.GroupeSanguin.A_POSITIF,
            personne_a_contacter="Test",
            date_inscription="2024-01-01"
        )

        self.client.force_authenticate(user=self.user_patient)

        # Accès à son propre dossier -> 200 OK
        res_own = self.client.get(f"/patients/{self.patient_record.id_patient}/")
        self.assertEqual(res_own.status_code, 200)
        self.assertEqual(res_own.json()["idPatient"], self.patient_record.id_patient)

        # Accès au dossier d'un autre patient -> 403 Forbidden
        res_other = self.client.get(f"/patients/{other_patient.id_patient}/")
        self.assertEqual(res_other.status_code, 403)

    def test_patient_and_infirmier_cannot_delete_patient(self):
        """Ni le patient ni l'infirmier ne peuvent supprimer un dossier patient (réservé admin)."""
        # Patient -> 403 Forbidden
        self.client.force_authenticate(user=self.user_patient)
        res_pat = self.client.delete(f"/patients/{self.patient_record.id_patient}/")
        self.assertEqual(res_pat.status_code, 403)

        # Infirmier -> 403 Forbidden
        self.client.force_authenticate(user=self.infirmier)
        res_inf = self.client.delete(f"/patients/{self.patient_record.id_patient}/")
        self.assertEqual(res_inf.status_code, 403)

    def test_patient_soft_deleted_hidden_by_default_and_visible_with_all(self):
        """Un patient désactivé (actif=False) n'apparaît pas par défaut mais apparaît avec ?all=true."""
        self.client.force_authenticate(user=self.admin)
        # Soft delete
        self.user_patient.actif = False
        self.user_patient.save()

        # Liste par défaut -> vide (ou ne contient pas le patient désactivé)
        res_default = self.client.get("/patients/")
        self.assertEqual(res_default.status_code, 200)
        items = res_default.json().get("results", res_default.json())
        ids = [p["idPatient"] for p in items]
        self.assertNotIn(self.patient_record.id_patient, ids)

        # Liste avec ?all=true -> contient le patient désactivé
        res_all = self.client.get("/patients/?all=true")
        self.assertEqual(res_all.status_code, 200)
        items_all = res_all.json().get("results", res_all.json())
        ids_all = [p["idPatient"] for p in items_all]
        self.assertIn(self.patient_record.id_patient, ids_all)

    def test_staff_and_admin_can_read_numero_securite_sociale(self):
        """Médecin, Infirmier et Administrateur peuvent consulter le numéro de sécurité sociale complet."""
        for user in [self.medecin, self.infirmier, self.admin]:
            self.client.force_authenticate(user=user)
            res = self.client.get(f"/patients/{self.patient_record.id_patient}/")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            secu = data.get("numeroSecuriteSociale") or data.get("numero_securite_sociale")
            self.assertEqual(secu, "1920615000111")

    def test_patient_can_read_own_numero_securite_sociale(self):
        """Un patient connecté peut lire son propre numéro de sécurité sociale."""
        self.client.force_authenticate(user=self.user_patient)
        res = self.client.get(f"/patients/{self.patient_record.id_patient}/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        secu = data.get("numeroSecuriteSociale") or data.get("numero_securite_sociale")
        self.assertEqual(secu, "1920615000111")

    def test_unauthorized_user_serializer_masks_numero_securite_sociale(self):
        """Si un patient tente de sérialiser un autre patient, son numéro de sécurité sociale est masqué (None)."""
        from rest_framework.test import APIRequestFactory
        from patients.patientSerializers import PatientSerializer

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.user_patient  # user_patient sérialise un autre patient

        other_user = User.objects.create(
            nom="Autre", prenom="Patient", email="autre2@example.com",
            telephone="+224622998877", login="autre_pat2", motDePasseHash="hash",
            role=User.Role.PATIENT
        )
        other_patient = Patient.objects.create(
            id_utilisateur=other_user,
            date_naissance="1980-01-01",
            sexe=Patient.Sexe.FEMININ,
            adresse="Dixinn",
            groupe_sanguin=Patient.GroupeSanguin.B_POSITIF,
            numero_securite_sociale="2800101999000",
            personne_a_contacter="Proche",
            date_inscription="2024-01-01"
        )

        serializer = PatientSerializer(other_patient, context={"request": request})
        self.assertIsNone(serializer.data.get("numero_securite_sociale"))
        self.assertIsNone(serializer.data.get("numeroSecuriteSociale"))

    def test_patient_cannot_modify_numero_securite_sociale(self):
        """Un patient ne peut pas modifier son propre numéro de sécurité sociale (400 Bad Request)."""
        self.client.force_authenticate(user=self.user_patient)
        payload = {
            "numeroSecuriteSociale": "9999999999999"
        }
        res = self.client.patch(f"/patients/{self.patient_record.id_patient}/", payload, format="json")
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertTrue("numeroSecuriteSociale" in data or "numero_securite_sociale" in data)
        self.patient_record.refresh_from_db()
        self.assertEqual(self.patient_record.numero_securite_sociale, "1920615000111")

    def test_medecin_or_admin_can_modify_numero_securite_sociale(self):
        """Un médecin ou administrateur peut modifier le numéro de sécurité sociale d'un patient."""
        self.client.force_authenticate(user=self.medecin)
        payload = {
            "numeroSecuriteSociale": "1920615000222"
        }
        res = self.client.patch(f"/patients/{self.patient_record.id_patient}/", payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.patient_record.refresh_from_db()
        self.assertEqual(self.patient_record.numero_securite_sociale, "1920615000222")
