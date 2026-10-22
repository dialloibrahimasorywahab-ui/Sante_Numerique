from django.test import TestCase
from common.test_helpers import creer_test_utilisateur, creer_test_patient
from services.models import Service
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit

from sejour.models import Sejour
from sejour.sejourServices import SejourService
from mouvement.models import MouvementPatient
from mouvement.mouvementServices import MouvementService
from evenement.models import EvenementParcours


class MouvementTests(TestCase):
    def setUp(self):
        self.user = creer_test_utilisateur("mvt_user", role="ADMINISTRATEUR")
        self.urgences = Service.objects.create(nom_service="Urgences")
        self.labo = Service.objects.create(nom_service="Laboratoire")
        self.cardio = Service.objects.create(nom_service="Cardiologie")

        self.patient = creer_test_patient("fatoumata_sylla")

        self.batiment = Batiment.objects.create(nom="Bâtiment Central")
        self.chambre = Chambre.objects.create(numero_chambre=102, batiment=self.batiment)
        self.lit = Lit.objects.create(chambre=self.chambre, numero_lit="L102-1", etat="DISPONIBLE")

        self.sejour = SejourService().admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.urgences.id_service,
                "motif_admission": "Bilan d'urgence",
            },
            user=self.user,
        )
        self.mvt_service = MouvementService()

    def test_parcours_urgences_labo_hospitalisation(self):
        """Scénario : Urgences -> Laboratoire -> Cardiologie avec lit."""
        mvt_labo = self.mvt_service.effectuer_transfert(
            sejour_id=self.sejour.id_sejour,
            data={
                "service": self.labo.id_service,
                "type_mouvement": MouvementPatient.TypeMouvement.DEPART_EXAMEN,
                "motif": "Prélèvement sanguin et analyses",
            },
            user=self.user,
        )
        self.assertEqual(mvt_labo.type_mouvement, MouvementPatient.TypeMouvement.DEPART_EXAMEN)
        self.assertEqual(mvt_labo.localisation_destination.service_id, self.labo.id_service)

        mvt_cardio = self.mvt_service.effectuer_transfert(
            sejour_id=self.sejour.id_sejour,
            data={
                "service": self.cardio.id_service,
                "chambre": self.chambre.id,
                "lit": self.lit.id,
                "type_mouvement": MouvementPatient.TypeMouvement.TRANSFERT_SERVICE,
                "motif": "Admission en hospitalisation cardiologique",
            },
            user=self.user,
        )

        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, "OCCUPE")
        self.assertEqual(mvt_cardio.localisation_destination.lit_id, self.lit.id)

        mouvements = list(self.sejour.mouvements.order_by("date_mouvement"))
        self.assertEqual(len(mouvements), 3)
        self.assertEqual(mouvements[0].type_mouvement, MouvementPatient.TypeMouvement.ADMISSION)
        self.assertEqual(mouvements[1].type_mouvement, MouvementPatient.TypeMouvement.DEPART_EXAMEN)
        self.assertEqual(mouvements[2].type_mouvement, MouvementPatient.TypeMouvement.TRANSFERT_SERVICE)

        self.assertTrue(self.sejour.evenements.filter(type_evenement=EvenementParcours.TypeEvenement.TRANSFERT_INTERNE).exists())
