from common.services import BaseService
from .models import Natalite
from .nataliteRepositories import NataliteRepository


class NataliteService(BaseService[Natalite]):

    def __init__(self):
        self.repository = NataliteRepository()
        super().__init__(repository=self.repository)

    def create_nouveau_ne(self, **data):
        return self.repository.createNouveauNe(**data)

    def create_nouveaune(self, **data):
        return self.create_nouveau_ne(**data)

    def get_nouveau_ne_by_id(self, nouveauNe_id):
        return self.repository.get_NouveauNeById(nouveauNe_id)

    def get_nouveauneById(self, nouveauNe_id):
        return self.get_nouveau_ne_by_id(nouveauNe_id)

    def get_all_nouveaux_nes(self, actif_only: bool = True):
        return self.repository.get_all_nouveaux_nes(actif_only=actif_only)

    def get_all_nouveau_ne(self, actif_only: bool = True):
        return self.get_all_nouveaux_nes(actif_only=actif_only)

    def get_nouveaux_nes_by_patient(self, patient_id, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_patient(patient_id, actif_only=actif_only)

    def get_nouveaux_nes_by_medecin(self, medecin_id, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_medecin(medecin_id, actif_only=actif_only)

    def get_natalities_by_sexe(self, sexe, actif_only: bool = True):
        return self.repository.get_natalities_by_sexe(sexe, actif_only=actif_only)

    def get_nouveaux_nes_by_date(self, date_naissance, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_date(date_naissance, actif_only=actif_only)

    def search_nouveaux_nes(self, query, actif_only: bool = True):
        return self.repository.search_nouveaux_nes(query, actif_only=actif_only)

    def update_nouveau_ne(self, nouveau_ne, **data):
        return self.repository.update_data_nouveau_ne(nouveau_ne, **data)

    def update_data_nouveau_ne(self, nouveau_ne, **data):
        return self.update_nouveau_ne(nouveau_ne, **data)

    def delete_nouveau_ne(self, nouveau_ne_or_id, hard=False):
        return self.repository.delete_nouveau_ne(nouveau_ne_or_id, hard=hard)