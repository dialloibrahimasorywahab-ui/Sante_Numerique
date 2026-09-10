from typing import Generic, TypeVar, Type, Optional, List, Any
from django.db import models
from django.db.models import QuerySet
from .repositories import BaseRepository

T = TypeVar('T', bound=models.Model)


class BaseService(Generic[T]):
    """
    Service de base générique fournissant la logique métier standardisée
    et la délégation propre aux repositories.
    """
    repository: BaseRepository[T]

    def __init__(self, repository: Optional[BaseRepository[T]] = None):
        if repository is not None:
            self.repository = repository

    def create(self, **data) -> T:
        """Crée une nouvelle entité via le repository."""
        return self.repository.create(**data)

    def get_by_id(self, pk: Any, select_related: Optional[List[str]] = None, prefetch_related: Optional[List[str]] = None) -> Optional[T]:
        """Récupère une entité par sa clé primaire."""
        return self.repository.get_by_id(pk, select_related=select_related, prefetch_related=prefetch_related)

    def get_all(self, actif_only: bool = True, select_related: Optional[List[str]] = None, prefetch_related: Optional[List[str]] = None) -> QuerySet[T]:
        """Récupère toutes les entités."""
        return self.repository.get_all(actif_only=actif_only, select_related=select_related, prefetch_related=prefetch_related)

    def search(self, query: str, search_fields: Optional[List[str]] = None, actif_only: bool = True, select_related: Optional[List[str]] = None) -> QuerySet[T]:
        """Recherche des entités selon les champs configurés."""
        fields = search_fields or getattr(self, 'search_fields', ['nom'])
        return self.repository.search(query, search_fields=fields, actif_only=actif_only, select_related=select_related)

    def update(self, instance: T, **data) -> T:
        """Met à jour une entité existante."""
        return self.repository.update(instance, **data)

    def delete(self, instance: T, hard: bool = False) -> bool:
        """Supprime ou désactive une entité selon le contrat standardisé (retourne True)."""
        return self.repository.delete(instance, hard=hard)
