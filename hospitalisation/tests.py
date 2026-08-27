# pyrefly: ignore [missing-import]
from django.test import TestCase
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.test import APIClient

# pyrefly: ignore [import-error]
from users.models import User
# pyrefly: ignore [import-error]
from patients.models import Patient
from medecin.models import Medecin
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit

from .models import Hospitalisation
from .hospitalisationRepositories import HospitalisationRepository
from .hospitalisationServices import HospitalisationService


class HospitalisationModelAndServiceTests(TestCase):

    def setUp(self):
        self.user_patient = User.objects.create(
            nom="Diallo",
            prenom="Mamadou",
            email="mamadou.diallo@example.com",
            telephone="+221771112233",
            login="mamadou_d",
            motDePasseHash="pass123",
            role=User.Role.PATIENT,
        )
        self.patient = Patient.objects.create(
            idUtilisateur=self.user_patient,
            dateNaissance="1990-01-01",
            sexe=Patient.Sexe.MASCULIN,
            adresse="Dakar",
            groupeSanguin=Patient.GroupeSanguin.O_POSITIF,
            personneAContacter="Awa Diallo",
            dateInscription="2024-01-01",
        )

        self.user_doctor = User.objects.create(
            nom="Kane",
            prenom="Ousmane",
            email="ousmane.kane@example.com",
            telephone="+221772223344",
            login="dr_ousmane",
            motDePasseHash="pass456",
            role=User.Role.MEDECIN,
        )
        self.medecin = Medecin.objects.create(
            idUtilisateur=self.user_doctor,
            specialite=Medecin.Specialite.GENERALISTE,
            numeroOrdre="ORD-1234",
            dateEmbauche="2020-01-01",
        )

        self.batiment = Batiment.objects.create(nom="Bâtiment Principal")
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=101,
            capacite=2
        )
        self.lit = Lit.objects.create(
            chambre=self.chambre,
            numero_lit="LIT-101-A",
            etat=Lit.EtatLit.DISPONIBLE
        )

        self.repository = HospitalisationRepository()
        self.service = HospitalisationService(repository=self.repository)

    def test_admettre_patient_service_occupies_lit(self):
        hosp = self.service.admettre_patient(
            patient=self.patient,
            medecin=self.medecin,
            lit=self.lit,
            motif="Fièvre sévère",
            statut=Hospitalisation.StatutHospitalisation.EN_COURS,
        )
        self.assertIsNotNone(hosp.id)
        self.assertEqual(hosp.statut, Hospitalisation.StatutHospitalisation.EN_COURS)
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.etat, Lit.EtatLit.OCCUPE)

    def test_cloturer_hospitalisation_frees_lit(self):
        hosp = self.service.admettre_patient(
            patient=self.patient,
            medecin=self.medecin,
            lit=self.lit,
            motif="Observation post-opératoire",
        )
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.etat, Lit.EtatLit.OCCUPE)

        closed_hosp = self.service.cloturer_hospitalisation(hosp.id, observation_finale="Patient guéri")
        self.assertEqual(closed_hosp.statut, Hospitalisation.StatutHospitalisation.TERMINEE)
        self.assertIsNotNone(closed_hosp.date_sortie)
        self.assertIn("Patient guéri", closed_hosp.observation)

        self.lit.refresh_from_db()
        self.assertEqual(self.lit.etat, Lit.EtatLit.DISPONIBLE)

    def test_invalid_dates_raises_value_error(self):
        now = timezone.now()
        yesterday = now - timezone.timedelta(days=1)
        with self.assertRaises(ValueError):
            self.service.admettre_patient(
                patient=self.patient,
                date_entree=now,
                date_sortie=yesterday
            )

    def test_admettre_patient_occupied_lit_raises_value_error(self):
        # Première admission
        self.service.admettre_patient(
            patient=self.patient,
            medecin=self.medecin,
            lit=self.lit,
            motif="Première admission",
            statut=Hospitalisation.StatutHospitalisation.EN_COURS,
        )

        # Deuxième patient
        user_pat2 = User.objects.create(
            nom="Ba", prenom="Fatou", email="fatou.ba@example.com",
            telephone="+221770001122", login="fatou_b", motDePasseHash="pass123",
            role=User.Role.PATIENT
        )
        patient2 = Patient.objects.create(idUtilisateur=user_pat2, dateNaissance="1995-02-02", sexe=Patient.Sexe.FEMININ, dateInscription="2024-01-01")

        # Tenter d'admettre le 2e patient sur le même lit déjà occupé
        with self.assertRaises(ValueError):
            self.service.admettre_patient(
                patient=patient2,
                medecin=self.medecin,
                lit=self.lit,
                motif="Deuxième admission concurrente",
            )

    def test_chambre_sync_statut_on_admission_and_discharge(self):
        # Chambre avec 1 lit disponible -> DISPONIBLE
        self.chambre.sync_statut()
        self.assertEqual(self.chambre.statut, Chambre.StatutChambre.DISPONIBLE)

        # Admission -> lit devient OCCUPE -> chambre devient OCCUPEE (capacite=1)
        hosp = self.service.admettre_patient(patient=self.patient, lit=self.lit)
        self.chambre.refresh_from_db()
        self.assertEqual(self.chambre.statut, Chambre.StatutChambre.OCCUPEE)

        # Clôture -> lit redevient DISPONIBLE -> chambre redevient DISPONIBLE
        self.service.cloturer_hospitalisation(hosp.id)
        self.chambre.refresh_from_db()
        self.assertEqual(self.chambre.statut, Chambre.StatutChambre.DISPONIBLE)

    def test_supprimer_hospitalisation_soft_and_hard(self):
        hosp = self.service.admettre_patient(patient=self.patient, lit=self.lit)
        self.assertTrue(self.service.supprimer_hospitalisation(hosp.id, hard=False))
        hosp.refresh_from_db()
        self.assertFalse(hosp.actif)
        self.assertEqual(hosp.statut, Hospitalisation.StatutHospitalisation.ANNULEE)

        self.assertTrue(self.service.supprimer_hospitalisation(hosp.id, hard=True))
        self.assertIsNone(self.repository.get_hospitalisation_by_id(hosp.id))


class HospitalisationAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_patient = User.objects.create(
            nom="Sarr",
            prenom="Aïssatou",
            email="aissatou.sarr@example.com",
            telephone="+221773334455",
            login="aissatou_s",
            motDePasseHash="pass789",
            role=User.Role.PATIENT,
        )
        self.patient = Patient.objects.create(
            idUtilisateur=self.user_patient,
            dateNaissance="1998-05-12",
            sexe=Patient.Sexe.FEMININ,
            dateInscription="2024-01-01",
        )

        self.user_doctor = User.objects.create(
            nom="Ndiaye",
            prenom="Ibrahima",
            email="ibrahima.ndiaye@example.com",
            telephone="+221774445566",
            login="dr_ibrahima",
            motDePasseHash="pass000",
            role=User.Role.MEDECIN,
        )
        self.medecin = Medecin.objects.create(
            idUtilisateur=self.user_doctor,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numeroOrdre="ORD-5566",
            dateEmbauche="2021-01-01",
        )

        self.batiment = Batiment.objects.create(nom="Bâtiment B")
        self.chambre = Chambre.objects.create(batiment=self.batiment, numero_chambre=202, capacite=1)
        self.lit = Lit.objects.create(chambre=self.chambre, numero_lit="LIT-202-A", etat=Lit.EtatLit.DISPONIBLE)

    def test_api_create_and_get_hospitalisation(self):
        url = "/hospitalisations/"
        payload = {
            "patient": self.patient.idPatient,
            "medecin": self.medecin.idMedecin,
            "lit": self.lit.idLit,
            "motif": "Douleurs thoraciques",
            "statut": "EN_COURS",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        hosp_id = response.data["id"]

        get_res = self.client.get(f"/hospitalisations/{hosp_id}/")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["motif"], "Douleurs thoraciques")

    def test_api_cloturer_hospitalisation(self):
        url = "/hospitalisations/"
        payload = {
            "patient": self.patient.idPatient,
            "medecin": self.medecin.idMedecin,
            "lit": self.lit.idLit,
            "motif": "Hospitalisation test clôture",
        }
        create_res = self.client.post(url, payload, format="json")
        hosp_id = create_res.data["id"]

        cloture_url = f"/hospitalisations/{hosp_id}/cloturer/"
        res = self.client.post(cloture_url, {"observation": "Patient rétabli"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["statut"], Hospitalisation.StatutHospitalisation.TERMINEE)
        self.assertIsNotNone(res.data["date_sortie"])

    def test_api_delete_hospitalisation(self):
        payload = {
            "patient": self.patient.idPatient,
            "motif": "Hospitalisation test suppression",
        }
        create_res = self.client.post("/hospitalisations/", payload, format="json")
        hosp_id = create_res.data["id"]

        del_res = self.client.delete(f"/hospitalisations/{hosp_id}/delete/")
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)

        hard_del_res = self.client.delete(f"/hospitalisations/{hosp_id}/delete/?hard=true")
        self.assertEqual(hard_del_res.status_code, status.HTTP_200_OK)
