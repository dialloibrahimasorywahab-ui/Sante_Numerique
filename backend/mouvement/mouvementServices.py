import logging
from typing import Any, Dict, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import MouvementPatient
from .mouvementRepositories import MouvementRepository

logger = logging.getLogger(__name__)


class MouvementService:
    """Service orchestrateur des transferts et mouvements de patients."""

    def __init__(self):
        self.repository = MouvementRepository()

    @transaction.atomic
    def effectuer_transfert(
        self,
        sejour_id: int,
        data: Dict[str, Any],
        user=None,
    ) -> MouvementPatient:
        """
        Orchestre le transfert d'un patient entre deux unités ou lits :
        1. Identifie la localisation active d'origine.
        2. Clôture l'origine et active la destination via LocalisationService.
        3. Met à jour le service responsable du séjour si nécessaire.
        4. Enregistre l'enregistrement médico-légal MouvementPatient.
        5. Trace l'événement dans EvenementParcours.
        """
        from sejour.models import Sejour
        from localisation.models import LocalisationPatient
        from localisation.localisationServices import LocalisationService
        from evenement.models import EvenementParcours

        sejour = Sejour.objects.filter(id_sejour=sejour_id).first()
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        if not sejour.is_active:
            raise ValidationError({"sejour": "Impossible d'effectuer un transfert sur un séjour non actif."})

        loc_origine = LocalisationPatient.objects.filter(sejour=sejour, est_actuelle=True).first()

        date_mouvement = data.get("date_mouvement") or timezone.now()
        type_mouvement = data.get("type_mouvement", MouvementPatient.TypeMouvement.TRANSFERT_SERVICE)
        motif = data.get("motif", "Transfert de service")
        commentaire = data.get("commentaire", "")

        # Affecter la nouvelle localisation
        localisation_service = LocalisationService()
        loc_destination = localisation_service.affecter_localisation(
            sejour_id=sejour.id_sejour,
            data={
                "service_id": data.get("service_id") or data.get("service"),
                "batiment_id": data.get("batiment_id") or data.get("batiment"),
                "chambre_id": data.get("chambre_id") or data.get("chambre"),
                "lit_id": data.get("lit_id") or data.get("lit"),
                "date_debut": date_mouvement,
                "motif": motif,
                "commentaire": commentaire,
            },
            user=user,
        )

        # Mise à jour du séjour : passage au statut TRANSFERE et mise à jour du service responsable
        update_fields = ["updated_at", "statut"]
        sejour.statut = Sejour.StatutSejour.TRANSFERE
        if loc_destination.service_id and loc_destination.service_id != sejour.service_responsable_id:
            sejour.service_responsable_id = loc_destination.service_id
            update_fields.append("service_responsable_id")
        sejour.save(update_fields=update_fields)

        # Création du mouvement
        mouvement = MouvementPatient.objects.create(
            sejour=sejour,
            localisation_origine=loc_origine,
            localisation_destination=loc_destination,
            date_mouvement=date_mouvement,
            type_mouvement=type_mouvement,
            motif=motif,
            commentaire=commentaire,
            enregistre_par=user,
        )

        # Timeline événement
        from_str = loc_origine.format_medical() if loc_origine else "Accueil / Admissions"
        to_str = loc_destination.format_medical()
        service_dest = (
            loc_destination.service.get_nom_service_display()
            if hasattr(loc_destination.service, "get_nom_service_display")
            else str(loc_destination.service)
        )
        titre = f"Transfert vers {service_dest}"
        description = f"Transfert depuis {from_str} vers {to_str}."
        if motif:
            description += f" Motif : {motif}."
        if commentaire:
            description += f" Note : {commentaire}."

        EvenementParcours.objects.create(
            sejour=sejour,
            type_evenement=EvenementParcours.TypeEvenement.TRANSFERT_INTERNE,
            titre=titre,
            description=description,
            date_evenement=date_mouvement,
            declare_par=user,
            importance=EvenementParcours.NiveauImportance.INFO,
            donnees_additionnelles={
                "mouvement_id": mouvement.id,
                "origine_id": loc_origine.id if loc_origine else None,
                "destination_id": loc_destination.id,
            },
        )

        logger.info(f"Transfert réussi pour le séjour {sejour.reference} (Mouvement #{mouvement.id})")
        return mouvement
