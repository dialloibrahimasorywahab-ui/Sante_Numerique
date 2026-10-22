import logging
from typing import Any, Dict
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import EvenementParcours
from .evenementRepositories import EvenementRepository

logger = logging.getLogger(__name__)


class EvenementService:
    """Service d'enregistrement et de consultation des jalons du parcours patient."""

    def __init__(self):
        self.repository = EvenementRepository()

    def enregistrer_evenement(self, sejour_id: int, data: Dict[str, Any], user=None) -> EvenementParcours:
        """Ajoute un jalon d'événement horodaté dans la timeline du séjour."""
        from sejour.models import Sejour

        sejour = Sejour.objects.filter(id_sejour=sejour_id).first()
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        titre = data.get("titre")
        if not titre:
            raise ValidationError({"titre": "Le titre de l'événement est requis."})

        evenement = EvenementParcours(
            sejour=sejour,
            type_evenement=data.get("type_evenement", EvenementParcours.TypeEvenement.OBSERVATION),
            titre=titre,
            description=data.get("description", ""),
            date_evenement=data.get("date_evenement") or timezone.now(),
            declare_par=user,
            importance=data.get("importance", EvenementParcours.NiveauImportance.INFO),
            donnees_additionnelles=data.get("donnees_additionnelles") or {},
        )
        evenement.full_clean()
        evenement.save()
        logger.info(f"Événement #{evenement.id} consigné pour le séjour {sejour.reference}")
        return evenement
