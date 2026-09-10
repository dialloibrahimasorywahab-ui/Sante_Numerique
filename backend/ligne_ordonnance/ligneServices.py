from typing import Optional, List
from django.db.models import QuerySet
from common.services import BaseService
from .models import LigneOrdonnance
from .ligneRepositories import LigneOrdonnanceRepository


class LigneOrdonnanceService(BaseService[LigneOrdonnance]):
    """
    Service métier pour la gestion des lignes d'ordonnances.
    """
    def __init__(self):
        self.repository = LigneOrdonnanceRepository()
        super().__init__(repository=self.repository)

    def create_ligne(self, **data) -> LigneOrdonnance:
        """Crée une nouvelle ligne de prescription."""
        return self.create(**data)

    def get_ligne(self, pk: int) -> Optional[LigneOrdonnance]:
        """Récupère une ligne par sa clé primaire."""
        return self.get_by_id(pk, select_related=['ordonnance'])

    def get_all_lignes(self, actif_only: bool = True) -> QuerySet[LigneOrdonnance]:
        """Récupère toutes les lignes de prescriptions."""
        return self.get_all(actif_only=actif_only, select_related=['ordonnance'])

    def get_by_ordonnance(self, ordonnance_id: int, actif_only: bool = True) -> QuerySet[LigneOrdonnance]:
        """Récupère les lignes d'une ordonnance."""
        return self.repository.get_by_ordonnance(ordonnance_id, actif_only=actif_only)

    def search_lignes(self, query: str, actif_only: bool = True) -> QuerySet[LigneOrdonnance]:
        """Recherche dans les lignes de prescription."""
        return self.repository.search_lignes(query, actif_only=actif_only)

    def update_ligne(self, instance: LigneOrdonnance, **data) -> LigneOrdonnance:
        """Met à jour une ligne de prescription."""
        return self.update(instance, **data)

    def delete_ligne(self, instance: LigneOrdonnance, hard: bool = False) -> bool:
        """Supprime ou désactive une ligne de prescription."""
        return self.delete(instance, hard=hard)
