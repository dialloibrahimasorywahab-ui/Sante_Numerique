from common.repositories import BaseRepository
from .models import Batiment


class BatimentRepository(BaseRepository[Batiment]):

    def __init__(self):
        super().__init__(model=Batiment)

    def create_batiment(self, **data):
        return self.create(**data)

    def get_batiment(self, batiment_id):
        return self.get_by_id(batiment_id)

    def get_batiment_by_nom(self, nom):
        if not nom:
            return None
        try:
            return self.model.objects.get(nom__iexact=nom.strip())
        except self.model.DoesNotExist:
            return None

    def get_all_batiments(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only)

    def search_batiments(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=['nom', 'description'],
            actif_only=actif_only
        )

    def update_batiment(self, batiment, **data):
        return self.update(batiment, **data)

    def delete_batiment(self, batiment, hard=False):
        return self.delete(batiment, hard=hard)
