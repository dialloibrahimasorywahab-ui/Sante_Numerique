from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.test_helpers import creer_test_utilisateur, creer_test_patient
from services.models import Service
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit

from sejour.models import Sejour
from sejour.sejourServices import SejourService
from localisation.models import LocalisationPatient
from localisation.localisationServices import LocalisationService


class LocalisationTests(TestCase):
    def setUp(self):
        self.user = creer_test_utilisateur("loc_admin", role="ADMINISTRATEUR")
        self.service_urgences = Service.objects.create(nom_service="Urgences")
        self.service_chirurgie = Service.objects.create(nom_service="Chirurgie")

        self.patient = creer_test_patient("oumar_barry")

        self.batiment_a = Batiment.objects.create(nom="Bâtiment A")
        self.batiment_b = Batiment.objects.create(nom="Bâtiment B")

        self.chambre_1 = Chambre.objects.create(
            batiment=self.batiment_a,
            numero_chambre=201,
        )
        self.chambre_autre = Chambre.objects.create(
            batiment=self.batiment_b,
            numero_chambre=301,
        )

        self.lit_libre = Lit.objects.create(chambre=self.chambre_1, numero_lit="L201-1", etat="DISPONIBLE")
        self.lit_occupe = Lit.objects.create(chambre=self.chambre_1, numero_lit="L201-2", etat="OCCUPE")

        self.sejour = SejourService().admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "motif_admission": "Traumatisme",
            },
            user=self.user,
        )
        self.loc_service = LocalisationService()

    def test_cannot_assign_already_occupied_bed(self):
        """Vérifie le rejet immédiat en cas d'affectation d'un lit déjà occupé."""
        with self.assertRaises(ValidationError):
            self.loc_service.affecter_localisation(
                sejour_id=self.sejour.id_sejour,
                data={
                    "service": self.service_chirurgie.id_service,
                    "lit": self.lit_occupe.id,
                },
                user=self.user,
            )

    def test_spatial_coherence_validation(self):
        """Vérifie la cohérence entre Lit, Chambre et Bâtiment."""
        loc = LocalisationPatient(
            sejour=self.sejour,
            service=self.service_chirurgie,
            batiment=self.batiment_a,
            chambre=self.chambre_autre,
            date_debut=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            loc.clean()

    def test_successful_bed_allocation_and_old_bed_release(self):
        """Vérifie l'affectation à un lit libre et la transition des statuts."""
        loc = self.loc_service.affecter_localisation(
            sejour_id=self.sejour.id_sejour,
            data={
                "service": self.service_chirurgie.id_service,
                "lit": self.lit_libre.id,
            },
            user=self.user,
        )
        self.assertEqual(loc.lit_id, self.lit_libre.id)
        self.lit_libre.refresh_from_db()
        self.assertEqual(self.lit_libre.statut, "OCCUPE")
