from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import FraisConsultation
from .fraisServices import FraisConsultationService


class FraisConsultationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.service = FraisConsultationService()

    def test_creer_frais_and_reglement(self):
        frais = self.service.creer_frais(montant=15000.0, description="Consultation Cardiologie")
        self.assertEqual(frais.montant, 15000.0)
        self.assertEqual(frais.statut, FraisConsultation.StatutPaiement.EN_ATTENTE)

        paid_frais = self.service.enregistrer_reglement(frais.id)
        self.assertEqual(paid_frais.statut, FraisConsultation.StatutPaiement.PAYE)
        self.assertIsNotNone(paid_frais.date_paiement)

    def test_frais_negative_montant_rejected(self):
        with self.assertRaises(ValueError):
            self.service.creer_frais(montant=-500.0)

    def test_api_frais_crud(self):
        post_res = self.client.post("/frais_consultations/", {"montant": 20000.0, "description": "Bilan général"}, format="json")
        self.assertEqual(post_res.status_code, status.HTTP_201_CREATED)
        frais_id = post_res.data["id"]

        payer_res = self.client.post(f"/frais_consultations/{frais_id}/payer/")
        self.assertEqual(payer_res.status_code, status.HTTP_200_OK)
        self.assertEqual(payer_res.data["statut"], FraisConsultation.StatutPaiement.PAYE)
