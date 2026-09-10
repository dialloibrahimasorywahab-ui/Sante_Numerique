from django.db.models import Q
from common.repositories import BaseRepository
from .models import Mortalite


class MortaliteRepository(BaseRepository[Mortalite]):

    def __init__(self):
        super().__init__(model=Mortalite)

    def createDeces(self, **data):
        return self.create(**data)

    def get_DecesById(self, deces_id):
        return self.get_by_id(
            deces_id,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def get_all_mortalites(self, actif_only: bool = True):
        return self.get_all(
            actif_only=actif_only,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def get_mortalites_by_patient(self, patient_id, actif_only: bool = True):
        return self.get_all_mortalites(actif_only=actif_only).filter(id_patient_id=patient_id)

    def get_mortalites_by_medecin(self, medecin_id, actif_only: bool = True):
        return self.get_all_mortalites(actif_only=actif_only).filter(id_medecin_id=medecin_id)

    def get_mortalites_by_date(self, date_deces, actif_only: bool = True):
        return self.get_all_mortalites(actif_only=actif_only).filter(date_deces=date_deces)

    def search_mortalites(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=[
                'cause_deces',
                'lieu_deces',
                'observation',
                'id_patient__id_utilisateur__nom',
                'id_patient__id_utilisateur__prenom'
            ],
            actif_only=actif_only,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def update_deces(self, deces, **data):
        return self.update(deces, **data)

    def delete_deces(self, deces_or_id, hard=False):
        instance = deces_or_id if isinstance(deces_or_id, Mortalite) else self.get_DecesById(deces_or_id)
        if instance:
            return self.delete(instance, hard=hard)
        return False
