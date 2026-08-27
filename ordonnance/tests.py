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
        self.assertGreaterEqual(len(res.data), 1)

        search_res = self.client.get("/ordonnances/", {"search": "toux"})
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_res.data), 1)

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

