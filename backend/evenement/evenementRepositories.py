import logging
from typing import Optional
from django.db.models import QuerySet
from .models import EvenementParcours

logger = logging.getLogger(__name__)


class EvenementRepository:
    """Accès optimisé aux événements du parcours patient (timeline chronologique)."""

    def get_queryset(self, actif_only: bool = True) -> QuerySet[EvenementParcours]:
        qs = EvenementParcours.objects.select_related(
            "sejour",
            "sejour__patient",
            "declare_par",
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_by_id(self, event_id: int, actif_only: bool = True) -> Optional[EvenementParcours]:
        try:
            return self.get_queryset(actif_only=actif_only).get(id=event_id)
        except EvenementParcours.DoesNotExist:
            return None

    def get_all(
        self,
        sejour_id: Optional[int] = None,
        type_evenement: Optional[str] = None,
        importance: Optional[str] = None,
        actif_only: bool = True,
    ) -> QuerySet[EvenementParcours]:
        qs = self.get_queryset(actif_only=actif_only)
        if sejour_id:
            qs = qs.filter(sejour_id=sejour_id)
        if type_evenement:
            qs = qs.filter(type_evenement=type_evenement)
        if importance:
            qs = qs.filter(importance=importance)
        return qs
