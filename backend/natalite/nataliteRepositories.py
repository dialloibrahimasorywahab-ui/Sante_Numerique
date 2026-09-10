from django.db.models import Q
from common.repositories import BaseRepository
from .models import Natalite


class NataliteRepository(BaseRepository[Natalite]):

    def __init__(self):
        super().__init__(model=Natalite)

    def createNouveauNe(self, **data):
        return self.create(**data)

    def get_NouveauNeById(self, nouveauNe_id):
        return self.get_by_id(
            nouveauNe_id,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def get_all_nouveaux_nes(self, actif_only: bool = True):
        return self.get_all(
            actif_only=actif_only,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def get_nouveaux_nes_by_patient(self, patient_id, actif_only: bool = True):
        return self.get_all_nouveaux_nes(actif_only=actif_only).filter(id_patient_id=patient_id)

    def get_nouveaux_nes_by_medecin(self, medecin_id, actif_only: bool = True):
        return self.get_all_nouveaux_nes(actif_only=actif_only).filter(id_medecin_id=medecin_id)

    def get_natalities_by_sexe(self, sexe, actif_only: bool = True):
        return self.get_all_nouveaux_nes(actif_only=actif_only).filter(sexe=sexe)

    def get_nouveaux_nes_by_date(self, date_naissance, actif_only: bool = True):
        return self.get_all_nouveaux_nes(actif_only=actif_only).filter(date_naissance=date_naissance)

    def search_nouveaux_nes(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=[
                'prenom_nouveau_ne',
                'nom_nouveau_ne',
                'lieu_naissance',
                'observation'
            ],
            actif_only=actif_only,
            select_related=[
                'id_patient__id_utilisateur',
                'id_medecin__id_utilisateur'
            ]
        )

    def update_data_nouveau_ne(self, nouveau_ne, **data):
        return self.update(nouveau_ne, **data)

    def delete_nouveau_ne(self, nouveau_ne_or_id, hard=False):
        instance = nouveau_ne_or_id if isinstance(nouveau_ne_or_id, Natalite) else self.get_NouveauNeById(nouveau_ne_or_id)
        if instance:
            return self.delete(instance, hard=hard)
        return False