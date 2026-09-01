from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from consultation.models import Consultation
from .models import Ordonnance
from .ordonnanceServices import OrdonnanceService


class OrdonnanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_p = User.objects.create(
            nom="Diop", prenom="Awa", email="awa.diop@example.com",
            telephone="+221775556677", login="awa_d", motDePasseHash="pass123", role=User.Role.PATIENT
        )
        self.patient = Patient.objects.create(idUtilisateur=self.user_p, dateNaissance="1992-04-15", sexe=Patient.Sexe.FEMININ, dateInscription="2024-01-01")

        self.user_m = User.objects.create(
            nom="Touré", prenom="Ousmane", email="ousmane.toure@example.com",
            telephone="+221776667788", login="dr_ousmanet", motDePasseHash="pass456", role=User.Role.MEDECIN
        )
        self.medecin = Medecin.objects.create(idUtilisateur=self.user_m, specialite=Medecin.Specialite.GENERALISTE, dateEmbauche="2019-01-01")

        self.consultation = Consultation.objects.create(
            patient=self.patient, medecin=self.medecin, symptomes="Toux sèche", diagnostic="Bronchite"
        )
        self.service = OrdonnanceService()
        self.client.force_authenticate(user=self.user_m)

    def test_prescrire_ordonnance_service(self):
        ord_obj = self.service.prescrire_ordonnance(
            consultation=self.consultation,
            observation="Paracétamol 1g 3x/jour pendant 5 jours\nAmoxicilline 500mg"
        )
        self.assertIsNotNone(ord_obj.id)
        self.assertTrue(ord_obj.reference.startswith("ORD-"))
        self.assertIn("Paracétamol", ord_obj.observation)

    def test_api_ordonnance_crud(self):
        payload = {
            "consultation": self.consultation.idConsultation,
            "observation": "Ibuprofène 400mg"
        }
        res = self.client.post("/ordonnances/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ord_id = res.data["id"]

        get_res = self.client.get(f"/ordonnances/{ord_id}/")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertIn("Ibuprofène", get_res.data["observation"])

    def test_api_ordonnance_list_and_filters(self):
        ord_obj = self.service.prescrire_ordonnance(
            consultation=self.consultation,
            observation="Sirop contre la toux"
        )
        res = self.client.get("/ordonnances/", {"consultation_id": self.consultation.idConsultation})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data["results"]), 1)

        search_res = self.client.get("/ordonnances/", {"search": "toux"})
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        self.assertEqual(search_res.data["count"], 1)
        self.assertEqual(len(search_res.data["results"]), 1)

    def test_api_ordonnance_update_patch_and_delete(self):
        ord_obj = self.service.prescrire_ordonnance(
            consultation=self.consultation,
            observation="Vitamines C 500mg"
        )
        patch_res = self.client.patch(f"/ordonnances/{ord_obj.id}/", {"observation": "Vitamines C 1000mg"}, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["observation"], "Vitamines C 1000mg")

        del_res = self.client.delete(f"/ordonnances/{ord_obj.id}/delete/")
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)

        hard_del_res = self.client.delete(f"/ordonnances/{ord_obj.id}/delete/?hard=true")
        self.assertEqual(hard_del_res.status_code, status.HTTP_200_OK)

        not_found_res = self.client.get(f"/ordonnances/{ord_obj.id}/")
        self.assertEqual(not_found_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_based_ordonnance_access(self):
        # Médecin 1 (self.user_m / self.medecin) prescrit une ordonnance
        ord_m1 = self.service.prescrire_ordonnance(
            consultation=self.consultation,
            observation="Ordonnance Médecin 1"
        )

        # Création d'un second médecin avec sa propre consultation et ordonnance
        user_m2 = User.objects.create(
            nom="Sylla", prenom="Abdoulaye", email="abdoulaye.sylla@example.com",
            telephone="+221770002233", login="dr_sylla", motDePasseHash="pass456", role=User.Role.MEDECIN
        )
        medecin2 = Medecin.objects.create(
            idUtilisateur=user_m2,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numeroOrdre="ORD-MED-ORD-02",
            dateEmbauche="2021-01-01"
        )
        cons_m2 = Consultation.objects.create(patient=self.patient, medecin=medecin2, diagnostic="Angine")
        ord_m2 = self.service.prescrire_ordonnance(
            consultation=cons_m2,
            observation="Ordonnance Médecin 2"
        )

        # 1. MEDECIN (dr_ousmanet / self.user_m)
        self.client.force_authenticate(user=self.user_m)
        # Liste : ne voit que ses ordonnances
        res_list = self.client.get("/ordonnances/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data["count"], 1)
        self.assertEqual(res_list.data["results"][0]["id"], ord_m1.id)

        # GET detail sur sa propre ordonnance -> 200
        self.assertEqual(self.client.get(f"/ordonnances/{ord_m1.id}/").status_code, status.HTTP_200_OK)
        # GET detail sur l'ordonnance d'un autre médecin -> 403
        self.assertEqual(self.client.get(f"/ordonnances/{ord_m2.id}/").status_code, status.HTTP_403_FORBIDDEN)

        # Tentative de prescrire pour la consultation d'un autre médecin -> 403
        payload_other = {"consultation": cons_m2.idConsultation, "observation": "Intrusion"}
        self.assertEqual(self.client.post("/ordonnances/", payload_other, format="json").status_code, status.HTTP_403_FORBIDDEN)

        # Tentative de modifier l'ordonnance d'un autre médecin -> 403
        self.assertEqual(self.client.patch(f"/ordonnances/{ord_m2.id}/", {"observation": "Modif frauduleuse"}, format="json").status_code, status.HTTP_403_FORBIDDEN)

        # Tentative de supprimer l'ordonnance d'un autre médecin -> 403
        self.assertEqual(self.client.delete(f"/ordonnances/{ord_m2.id}/delete/").status_code, status.HTTP_403_FORBIDDEN)

        # 2. INFIRMIER
        user_inf = User.objects.create(
            nom="Fall", prenom="Mariama", email="mariama.fall@example.com",
            telephone="+221770004455", login="inf_mariama", motDePasseHash="pass123", role=User.Role.INFIRMIER
        )
        self.client.force_authenticate(user=user_inf)
        # GET liste globale -> 403 Forbidden
        self.assertEqual(self.client.get("/ordonnances/").status_code, status.HTTP_403_FORBIDDEN)
        # GET detail unitaire -> 200 OK (pour administrer les soins)
        self.assertEqual(self.client.get(f"/ordonnances/{ord_m1.id}/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(f"/ordonnances/{ord_m2.id}/").status_code, status.HTTP_200_OK)
        # POST/PUT/DELETE -> 403 Forbidden
        self.assertEqual(self.client.post("/ordonnances/", {"consultation": self.consultation.idConsultation}, format="json").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(f"/ordonnances/{ord_m1.id}/", {"observation": "Modif inf"}, format="json").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"/ordonnances/{ord_m1.id}/delete/").status_code, status.HTTP_403_FORBIDDEN)

        # 3. PATIENT (self.user_p)
        self.client.force_authenticate(user=self.user_p)
        # Liste : voit ses propres ordonnances
        res_pat = self.client.get("/ordonnances/")
        self.assertEqual(res_pat.status_code, status.HTTP_200_OK)
        self.assertEqual(res_pat.data["count"], 2)
        # Détail sur sa propre ordonnance -> 200
        self.assertEqual(self.client.get(f"/ordonnances/{ord_m1.id}/").status_code, status.HTTP_200_OK)

        # Création d'un autre patient
        user_p2 = User.objects.create(
            nom="Gueye", prenom="Aliou", email="aliou.gueye@example.com",
            telephone="+221770006677", login="aliou_g", motDePasseHash="pass123", role=User.Role.PATIENT
        )
        patient2 = Patient.objects.create(idUtilisateur=user_p2, dateNaissance="1988-11-20", sexe=Patient.Sexe.MASCULIN, dateInscription="2024-01-01")
        cons_p2 = Consultation.objects.create(patient=patient2, medecin=self.medecin, diagnostic="Grippe")
        ord_p2 = self.service.prescrire_ordonnance(consultation=cons_p2, observation="Ordonnance Patient 2")

        # Patient 1 tente d'accéder à l'ordonnance de Patient 2 -> 403 Forbidden
        self.assertEqual(self.client.get(f"/ordonnances/{ord_p2.id}/").status_code, status.HTTP_403_FORBIDDEN)
        # Patient tente d'écrire ou supprimer -> 403 Forbidden
        self.assertEqual(self.client.post("/ordonnances/", {"consultation": self.consultation.idConsultation}, format="json").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"/ordonnances/{ord_m1.id}/delete/").status_code, status.HTTP_403_FORBIDDEN)

        # 4. ADMINISTRATEUR
        user_admin = User.objects.create(
            nom="Admin", prenom="General", email="admin_gen@example.com",
            telephone="+221770008899", login="admin_general", motDePasseHash="pass123", role=User.Role.ADMINISTRATEUR
        )
        self.client.force_authenticate(user=user_admin)
        res_adm = self.client.get("/ordonnances/")
        self.assertEqual(res_adm.status_code, status.HTTP_200_OK)
        # L'administrateur voit l'ensemble (3 ordonnances)
        self.assertEqual(res_adm.data["count"], 3)
        self.assertEqual(self.client.get(f"/ordonnances/{ord_p2.id}/").status_code, status.HTTP_200_OK)


