from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status

from common.test_helpers import creer_test_utilisateur, creer_test_patient
from services.models import Service
from medecin.models import Medecin
from personnel.models import Personnel
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit

from sejour.models import Sejour, DemandeAnalyse
from sejour.sejourServices import SejourService
from localisation.models import LocalisationPatient
from mouvement.models import MouvementPatient
from evenement.models import EvenementParcours


class SejourFlowIntegrationTests(TestCase):
    def setUp(self):
        self.admin_user = creer_test_utilisateur("admin_test", role="ADMINISTRATEUR")
        self.medecin_user = creer_test_utilisateur("medecin_test", role="MEDECIN")
        self.infirmier_user = creer_test_utilisateur("infirmier_test", role="INFIRMIER")

        self.service_urgences = Service.objects.create(nom_service="Urgences", actif=True)
        self.service_cardio = Service.objects.create(nom_service="Cardiologie", actif=True)

        self.medecin = Medecin.objects.create(
            id_utilisateur=self.medecin_user,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numero_ordre="MED-2026-001",
            date_embauche="2024-01-01",
        )

        self.patient = creer_test_patient("aissatou_bah")

        self.batiment = Batiment.objects.create(nom="Pavillon Médecine", actif=True)
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=101,
            capacite=2,
        )
        self.lit_1 = Lit.objects.create(chambre=self.chambre, numero_lit="L101-A", etat="DISPONIBLE")
        self.lit_2 = Lit.objects.create(chambre=self.chambre, numero_lit="L101-B", etat="DISPONIBLE")

        self.service = SejourService()
        self.client = APIClient()

    def test_admission_standard_creates_sejour_localisation_mouvement_and_evenement(self):
        """Vérifie que l'admission initialise le séjour et l'ensemble de ses traces."""
        sejour = self.service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "type_prise_en_charge": Sejour.TypePriseEnCharge.URGENCE,
                "motif_admission": "Douleurs thoraciques aiguës",
            },
            user=self.admin_user,
        )

        self.assertIsNotNone(sejour.id_sejour)
        self.assertTrue(sejour.reference.startswith("S-"))
        self.assertEqual(sejour.statut, Sejour.StatutSejour.EN_COURS)
        self.assertTrue(sejour.is_active)

        loc = sejour.localisation_actuelle
        self.assertIsNotNone(loc)
        self.assertEqual(loc.service_id, self.service_urgences.id_service)
        self.assertTrue(loc.est_actuelle)

        mouvement = sejour.mouvements.first()
        self.assertIsNotNone(mouvement)
        self.assertEqual(mouvement.type_mouvement, MouvementPatient.TypeMouvement.ADMISSION)
        self.assertIsNone(mouvement.localisation_origine)
        self.assertEqual(mouvement.localisation_destination_id, loc.id)

        event = sejour.evenements.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.type_evenement, EvenementParcours.TypeEvenement.ADMISSION)

    def test_duplicate_active_sejour_is_rejected(self):
        """Vérifie qu'un patient ne peut pas avoir deux séjours actifs simultanés."""
        self.service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "motif_admission": "Premier séjour",
            },
            user=self.admin_user,
        )

        with self.assertRaises(ValidationError):
            self.service.admettre_patient(
                data={
                    "patient": self.patient.id_patient,
                    "service_responsable": self.service_cardio.id_service,
                    "motif_admission": "Deuxième séjour simultané",
                },
                user=self.admin_user,
            )

    def test_discharge_frees_bed_and_terminates_sejour(self):
        """Vérifie que la clôture de sortie libère le lit et clôture les localisations."""
        sejour = self.service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_cardio.id_service,
                "batiment": self.batiment.id_batiment,
                "chambre": self.chambre.id,
                "lit": self.lit_1.id,
                "motif_admission": "Hospitalisation cardio",
            },
            user=self.admin_user,
        )

        self.lit_1.refresh_from_db()
        self.assertEqual(self.lit_1.statut, "OCCUPE")

        sejour_clos = self.service.enregistrer_sortie(
            sejour_id=sejour.id_sejour,
            user=self.admin_user,
            motif_sortie="Guérison complète",
        )

        self.assertEqual(sejour_clos.statut, Sejour.StatutSejour.TERMINE)
        self.assertIsNotNone(sejour_clos.date_sortie)

        self.lit_1.refresh_from_db()
        self.assertEqual(self.lit_1.statut, "DISPONIBLE")
        self.assertFalse(sejour_clos.localisations.filter(est_actuelle=True).exists())

    def test_api_endpoints_permissions_and_synthese(self):
        """Vérifie les endpoints REST API et le dossier de synthèse 360°."""
        sejour = self.service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "motif_admission": "API Test Admission",
            },
            user=self.admin_user,
        )

        res = self.client.get(f"/sejours/{sejour.id_sejour}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(f"/sejours/{sejour.id_sejour}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["reference"], sejour.reference)

        res_synthese = self.client.get(f"/sejours/{sejour.id_sejour}/dossier-synthese/")
        self.assertEqual(res_synthese.status_code, status.HTTP_200_OK)
        self.assertIn("sejour", res_synthese.data)
        self.assertIn("localisation_actuelle", res_synthese.data)
        self.assertIn("mouvements", res_synthese.data)
        self.assertIn("evenements", res_synthese.data)
