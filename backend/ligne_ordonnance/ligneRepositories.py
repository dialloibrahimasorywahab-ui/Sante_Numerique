from typing import Optional
from django.db.models import QuerySet
from common.repositories import BaseRepository
from .models import LigneOrdonnance


class LigneOrdonnanceRepository(BaseRepository[LigneOrdonnance]):
    """
    Repository pour l'accès aux données des lignes d'ordonnances.
    """
    def __init__(self):
        super().__init__(model=LigneOrdonnance)

    def get_by_ordonnance(self, ordonnance_id: int, actif_only: bool = True) -> QuerySet[LigneOrdonnance]:
        """Récupère toutes les lignes associées à une ordonnance donnée."""
        qs = self.model.objects.filter(ordonnance_id=ordonnance_id).select_related('ordonnance')
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def search_lignes(self, query: str, actif_only: bool = True) -> QuerySet[LigneOrdonnance]:
        """Recherche des lignes de prescription par nom de médicament, forme ou posologie."""
        return self.search(
            query=query,
            search_fields=['medicament', 'forme', 'posologie', 'dosage'],
            actif_only=actif_only,
            select_related=['ordonnance']
        )
