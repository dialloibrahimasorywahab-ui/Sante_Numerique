import logging
from typing import Optional
from django.db.models import QuerySet
from .models import MouvementPatient

logger = logging.getLogger(__name__)


class MouvementRepository:
    """Accès aux données et traçabilité médico-légale des mouvements de patients."""

    def get_queryset(self) -> QuerySet[MouvementPatient]:
        return MouvementPatient.objects.select_related(
            "sejour",
            "sejour__patient",
            "localisation_origine",
            "localisation_origine__service",
            "localisation_origine__chambre",
            "localisation_origine__lit",
            "localisation_destination",
            "localisation_destination__service",
            "localisation_destination__chambre",
            "localisation_destination__lit",
            "enregistre_par",
        )

    def get_by_id(self, mouvement_id: int) -> Optional[MouvementPatient]:
        try:
            return self.get_queryset().get(id=mouvement_id)
        except MouvementPatient.DoesNotExist:
            return None

    def get_all(
        self,
        sejour_id: Optional[int] = None,
        type_mouvement: Optional[str] = None,
    ) -> QuerySet[MouvementPatient]:
        qs = self.get_queryset()
        if sejour_id:
            qs = qs.filter(sejour_id=sejour_id)
        if type_mouvement:
            qs = qs.filter(type_mouvement=type_mouvement)
        return qs
