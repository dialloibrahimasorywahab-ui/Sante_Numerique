from typing import Generic, TypeVar, Type, Optional, List, Any
from django.db import models
from django.db.models import Q, QuerySet

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    """
    Repository de base générique fournissant les opérations CRUD standardisées
    et des helpers de recherche pour toutes les applications du projet.
    """
    model: Type[T]

    def __init__(self, model: Optional[Type[T]] = None):
        if model is not None:
            self.model = model

    def create(self, **data) -> T:
        """Crée et persiste une nouvelle instance du modèle."""
        return self.model.objects.create(**data)

    def get_by_id(self, pk: Any, select_related: Optional[List[str]] = None, prefetch_related: Optional[List[str]] = None) -> Optional[T]:
        """Récupère une instance par sa clé primaire (pk) avec optimisations optionnelles."""
        try:
            qs: QuerySet[T] = self.model.objects.all()
            if select_related:
                qs = qs.select_related(*select_related)
            if prefetch_related:
                qs = qs.prefetch_related(*prefetch_related)
            return qs.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def get_all(self, actif_only: bool = True, select_related: Optional[List[str]] = None, prefetch_related: Optional[List[str]] = None) -> QuerySet[T]:
        """Retourne un QuerySet de toutes les instances, avec filtrage optionnel par actif."""
        qs: QuerySet[T] = self.model.objects.all()
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)

        if actif_only:
            field_names = [f.name for f in self.model._meta.get_fields()]
            if 'actif' in field_names:
                qs = qs.filter(actif=True)
            elif 'id_utilisateur' in field_names:
                qs = qs.filter(id_utilisateur__actif=True)

        return qs

    def search(self, query: str, search_fields: List[str], actif_only: bool = True, select_related: Optional[List[str]] = None) -> QuerySet[T]:
        """Effectue une recherche textuelle multi-champs insensible à la casse."""
        clean_q = str(query).strip() if query else ""
        if not clean_q:
            return self.get_all(actif_only=actif_only, select_related=select_related)

        q_filter = Q()
        for field in search_fields:
            q_filter |= Q(**{f"{field}__icontains": clean_q})

        qs: QuerySet[T] = self.model.objects.filter(q_filter)
        if select_related:
            qs = qs.select_related(*select_related)

        if actif_only:
            field_names = [f.name for f in self.model._meta.get_fields()]
            if 'actif' in field_names:
                qs = qs.filter(actif=True)
            elif 'id_utilisateur' in field_names:
                qs = qs.filter(id_utilisateur__actif=True)

        return qs

    def update(self, instance: T, **data) -> T:
        """Met à jour les attributs d'une instance et la sauvegarde."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, instance: T, hard: bool = False) -> bool:
        """
        Supprime définitivement (hard=True) ou désactive logiquement (soft-delete, hard=False)
        une entité de manière cohérente et atomique. Retourne True en cas de succès.
        """
        field_names = [f.name for f in self.model._meta.get_fields()]

        if hard:
            user = getattr(instance, 'id_utilisateur', None) or getattr(instance, 'idUtilisateur', None)
            instance.delete()
            if user and hasattr(user, 'delete'):
                user.delete()
            return True

        # Soft delete
        if 'actif' in field_names:
            setattr(instance, 'actif', False)
            instance.save(update_fields=['actif'])

        user = getattr(instance, 'id_utilisateur', None) or getattr(instance, 'idUtilisateur', None)
        if user and hasattr(user, 'actif'):
            user.actif = False
            user.save(update_fields=['actif'])

        return True
