import logging
from typing import Optional
from django.db.models import QuerySet
from .models import LocalisationPatient

logger = logging.getLogger(__name__)


class LocalisationRepository:
    """Accès aux données et requêtes d'optimisation pour la localisation spatiale des patients."""

    def get_queryset(self) -> QuerySet[LocalisationPatient]:
        return LocalisationPatient.objects.select_related(
            "sejour",
            "sejour__patient",
            "service",
            "batiment",
            "chambre",
            "lit",
            "enregistre_par",
        )

    def get_by_id(self, loc_id: int) -> Optional[LocalisationPatient]:
        try:
            return self.get_queryset().get(id=loc_id)
        except LocalisationPatient.DoesNotExist:
            return None

    def get_actuelle_by_sejour(self, sejour_id: int) -> Optional[LocalisationPatient]:
        return self.get_queryset().filter(sejour_id=sejour_id, est_actuelle=True).first()

    def get_all(
        self,
        sejour_id: Optional[int] = None,
        service_id: Optional[int] = None,
        chambre_id: Optional[int] = None,
        lit_id: Optional[int] = None,
        est_actuelle: Optional[bool] = None,
    ) -> QuerySet[LocalisationPatient]:
        qs = self.get_queryset()
        if sejour_id:
            qs = qs.filter(sejour_id=sejour_id)
        if service_id:
            qs = qs.filter(service_id=service_id)
        if chambre_id:
            qs = qs.filter(chambre_id=chambre_id)
        if lit_id:
            qs = qs.filter(lit_id=lit_id)
        if est_actuelle is not None:
            qs = qs.filter(est_actuelle=est_actuelle)
        return qs
