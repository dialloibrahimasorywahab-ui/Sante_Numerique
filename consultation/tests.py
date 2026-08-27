from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from frais_consultation.models import FraisConsultation
from .models import Consultation
from .consultationServices import ConsultationService


class ConsultationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_p = User.objects.create(
            nom="Diallo", prenom="Aissatou", email="aissatou.diallo@example.com",
            telephone="+221770009988", login="aissatou_d", motDePasseHash="pass123", role=User.Role.PATIENT
        )
        self.patient = Patient.objects.create(idUtilisateur=self.user_p, dateNaissance="1995-02-10", sexe=Patient.Sexe.FEMININ, dateInscription="2024-01-01")

        self.user_m = User.objects.create(
            nom="Sow", prenom="Mamadou", email="mamadou.sow@example.com",
            telephone="+221770008877", login="dr_mamadou", motDePasseHash="pass456", role=User.Role.MEDECIN
        )
        self.medecin = Medecin.objects.create(idUtilisateur=self.user_m, specialite=Medecin.Specialite.PEDIATRIE, dateEmbauche="2020-01-01")
        self.frais = FraisConsultation.objects.create(montant=10000.0, description="Consultation Générale")
        self.service = ConsultationService()
        self.client.force_authenticate(user=self.user_m)

    def test_creer_consultation_service(self):
        cons = self.service.creer_consultation(
            patient=self.patient, medecin=self.medecin, frais=self.frais,
            symptomes="Fièvre", diagnostic="Grippe saisonnière"
        )
        self.assertIsNotNone(cons.id)
        self.assertEqual(cons.patient, self.patient)
        self.assertEqual(cons.diagnostic, "Grippe saisonnière")

    def test_api_consultation_crud(self):
        payload = {
            "patient": self.patient.idPatient,
            "medecin": self.medecin.idMedecin,
            "frais": self.frais.idFrais,
            "symptomes": "Maux de tête",
            "diagnostic": "Migraine"
        }
        res = self.client.post("/consultations/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cons_id = res.data["id"]

        get_res = self.client.get(f"/consultations/{cons_id}/")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["diagnostic"], "Migraine")

    def test_consultation_with_rdv_completes_rdv(self):
        from rendezvous.models import RendezVous
        rdv = RendezVous.objects.create(
            patient=self.patient,
            medecin=self.medecin,
            date_rdv="2026-09-20",
            heure="15:00:00",
            statut=RendezVous.StatutRendezVous.CONFIRME
        )

        cons = self.service.creer_consultation(
            patient=self.patient,
            medecin=self.medecin,
            rdv=rdv,
            diagnostic="Contrôle OK"
        )
        rdv.refresh_from_db()
        self.assertEqual(rdv.statut, RendezVous.StatutRendezVous.TERMINE)
        self.assertEqual(cons.rdv, rdv)

    def test_consultation_with_invalid_patient_rdv_raises_value_error(self):
        from rendezvous.models import RendezVous
        user_p2 = User.objects.create(
            nom="Kane", prenom="Awa", email="awa.kane@example.com",
            telephone="+221770007766", login="awa_k", motDePasseHash="pass123", role=User.Role.PATIENT
        )
        other_patient = Patient.objects.create(idUtilisateur=user_p2, dateNaissance="1998-03-03", sexe=Patient.Sexe.FEMININ, dateInscription="2024-01-01")

        rdv_other = RendezVous.objects.create(
            patient=other_patient,
            medecin=self.medecin,
            date_rdv="2026-09-21",
            heure="16:00:00",
            statut=RendezVous.StatutRendezVous.CONFIRME
        )

        with self.assertRaises(ValueError):
            self.service.creer_consultation(
                patient=self.patient,
                medecin=self.medecin,
                rdv=rdv_other,
                diagnostic="Erreur patient"
            )

    def test_role_based_consultation_access(self):
        # Création d'un second médecin et d'une autre consultation
        user_m2 = User.objects.create(
            nom="Ndiaye", prenom="Abdou", email="abdou.ndiaye@example.com",
            telephone="+221770005544", login="dr_abdou", motDePasseHash="pass456", role=User.Role.MEDECIN
        )
        medecin2 = Medecin.objects.create(
            idUtilisateur=user_m2,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numeroOrdre="ORD-MED-CONS-02",
            dateEmbauche="2021-01-01"
        )

        cons_m1 = self.service.creer_consultation(patient=self.patient, medecin=self.medecin, diagnostic="Cons Dr Mamadou")
        cons_m2 = self.service.creer_consultation(patient=self.patient, medecin=medecin2, diagnostic="Cons Dr Abdou")

        # 1. MEDECIN (dr_mamadou) ne voit que sa propre consultation
        self.client.force_authenticate(user=self.user_m)
        res_list = self.client.get("/consultations/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data["count"], 1)
        self.assertEqual(res_list.data["results"][0]["id"], cons_m1.id)

        # GET detail sur sa propre consultation -> 200
        self.assertEqual(self.client.get(f"/consultations/{cons_m1.id}/").status_code, status.HTTP_200_OK)
        # GET detail sur la consultation d'un autre médecin -> 403
        self.assertEqual(self.client.get(f"/consultations/{cons_m2.id}/").status_code, status.HTTP_403_FORBIDDEN)

        # 2. INFIRMIER
        user_inf = User.objects.create(
            nom="Ba", prenom="Fatou", email="fatou.ba@example.com",
            telephone="+221770003322", login="inf_fatou", motDePasseHash="pass123", role=User.Role.INFIRMIER
        )
        self.client.force_authenticate(user=user_inf)
        # GET liste globale -> 403 Forbidden
        self.assertEqual(self.client.get("/consultations/").status_code, status.HTTP_403_FORBIDDEN)
        # GET detail unitaire -> 200 OK
        self.assertEqual(self.client.get(f"/consultations/{cons_m1.id}/").status_code, status.HTTP_200_OK)
        # POST/DELETE -> 403 Forbidden
        self.assertEqual(self.client.post("/consultations/", {}, format="json").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"/consultations/{cons_m1.id}/delete/").status_code, status.HTTP_403_FORBIDDEN)

        # 3. PATIENT
        self.client.force_authenticate(user=self.user_p)
        res_pat = self.client.get("/consultations/")
        self.assertEqual(res_pat.status_code, status.HTTP_200_OK)
        # Voit ses 2 consultations (faites par Dr 1 et Dr 2)
        self.assertEqual(res_pat.data["count"], 2)
        self.assertEqual(self.client.get(f"/consultations/{cons_m1.id}/").status_code, status.HTTP_200_OK)
        # Patient ne peut pas créer ni supprimer
        self.assertEqual(self.client.post("/consultations/", {}, format="json").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"/consultations/{cons_m1.id}/delete/").status_code, status.HTTP_403_FORBIDDEN)

        # 4. ADMINISTRATEUR
        user_admin = User.objects.create(
            nom="Admin", prenom="Super", email="admin@example.com",
            telephone="+221770001100", login="admin_boss", motDePasseHash="pass123", role=User.Role.ADMINISTRATEUR
        )
        self.client.force_authenticate(user=user_admin)
        res_adm = self.client.get("/consultations/")
        self.assertEqual(res_adm.status_code, status.HTTP_200_OK)
        self.assertEqual(res_adm.data["count"], 2)

