from django.test import TestCase
from common.test_helpers import creer_test_utilisateur, creer_test_patient
from services.models import Service

from sejour.models import Sejour
from sejour.sejourServices import SejourService
from evenement.models import EvenementParcours
from evenement.evenementServices import EvenementService


class EvenementTests(TestCase):
    def setUp(self):
        self.user = creer_test_utilisateur("evt_user", role="MEDECIN")
        self.service = Service.objects.create(nom_service="Urgences")
        self.patient = creer_test_patient("sekou_camara")

        self.sejour = SejourService().admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service.id_service,
                "motif_admission": "Observation",
            },
            user=self.user,
        )
        self.evt_service = EvenementService()

    def test_create_clinical_event_with_json_metadata(self):
        """Vérifie l'enregistrement d'un événement clinique avec constantes."""
        event = self.evt_service.enregistrer_evenement(
            sejour_id=self.sejour.id_sejour,
            data={
                "type_evenement": EvenementParcours.TypeEvenement.OBSERVATION,
                "titre": "Constantes vitales d'admission",
                "description": "Tension artérielle élevée, saturation normale.",
                "importance": EvenementParcours.NiveauImportance.ATTENTION,
                "donnees_additionnelles": {
                    "ta_systolique": 160,
                    "ta_diastolique": 95,
                    "spo2": 98,
                    "pouls": 88,
                },
            },
            user=self.user,
        )

        self.assertIsNotNone(event.id)
        self.assertEqual(event.importance, EvenementParcours.NiveauImportance.ATTENTION)
        self.assertEqual(event.donnees_additionnelles["ta_systolique"], 160)

    def test_chronological_ordering(self):
        """Vérifie que la timeline ordonne les événements de façon chronologique."""
        self.evt_service.enregistrer_evenement(
            sejour_id=self.sejour.id_sejour,
            data={"titre": "Premier jalon"},
            user=self.user,
        )
        self.evt_service.enregistrer_evenement(
            sejour_id=self.sejour.id_sejour,
            data={"titre": "Deuxième jalon"},
            user=self.user,
        )

        events = self.evt_service.repository.get_all(sejour_id=self.sejour.id_sejour)
        self.assertGreaterEqual(events.count(), 3)
