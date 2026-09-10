from django.db.models import Q
from common.repositories import BaseRepository
from .models import Personnel


class PersonnelRepository(BaseRepository[Personnel]):
    """
    Repository pour l'accès aux données du personnel.
    Hérite des méthodes CRUD génériques de BaseRepository.
    """
    def __init__(self):
        super().__init__(model=Personnel)

    def createPersonnel(self, **data):
        return self.create(**data)

    def get_personnel(self, personnel_id):
        return self.get_by_id(personnel_id, select_related=['id_utilisateur', 'id_service'])

    def get_all_personnel(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only, select_related=['id_utilisateur', 'id_service'])

    def get_personnel_by_type(self, type_personnel, actif_only: bool = True):
        qs = self.model.objects.filter(type_personnel__iexact=type_personnel).select_related('id_utilisateur', 'id_service')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    def get_personnel_by_service(self, service_id, actif_only: bool = True):
        qs = self.model.objects.filter(id_service_id=service_id).select_related('id_utilisateur', 'id_service')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    def search_personnel(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=[
                'id_utilisateur__nom',
                'id_utilisateur__prenom',
                'id_utilisateur__email',
                'matricule',
                'type_personnel'
            ],
            actif_only=actif_only,
            select_related=['id_utilisateur', 'id_service']
        )

    def update_Personnel(self, personnel, **data):
        return self.update(personnel, **data)

    def delete_personnel(self, personnel, hard=False):
        return self.delete(personnel, hard=hard)
