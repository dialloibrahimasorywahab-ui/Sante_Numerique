from common.repositories import BaseRepository
from .models import Service


class ServiceRepository(BaseRepository[Service]):

    def __init__(self):
        super().__init__(model=Service)

    def createService(self, **data):
        return self.create(**data)

    def get_service(self, service_id):
        return self.get_by_id(service_id)

    def get_service_by_nom(self, nom_service):
        try:
            return self.model.objects.get(nom_service__iexact=nom_service)
        except self.model.DoesNotExist:
            return None

    def get_all_services(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only)

    def search_services(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=['nom_service', 'description'],
            actif_only=actif_only
        )

    def update_service(self, service, **data):
        return self.update(service, **data)

    def delete_service(self, service, hard=False):
        return self.delete(service, hard=hard)
