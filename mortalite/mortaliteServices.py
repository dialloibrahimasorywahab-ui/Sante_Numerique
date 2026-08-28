from .mortaliteRepositories import MortaliteRepository


class MortaliteService:
    def __init__(self):
        self.repository = MortaliteRepository()

    def create_deces(self, **data):
        return self.repository.createDeces(**data)

    def get_deces_by_id(self, deces_id):
        return self.repository.get_DecesById(deces_id)

    def get_all_mortalites(self, actif_only: bool = True):
        return self.repository.get_all_mortalites(actif_only=actif_only)

    def get_mortalites_by_patient(self, patient_id, actif_only: bool = True):
        return self.repository.get_mortalites_by_patient(patient_id, actif_only=actif_only)

    def get_mortalites_by_medecin(self, medecin_id, actif_only: bool = True):
        return self.repository.get_mortalites_by_medecin(medecin_id, actif_only=actif_only)

    def get_mortalites_by_date(self, date_deces, actif_only: bool = True):
        return self.repository.get_mortalites_by_date(date_deces, actif_only=actif_only)

    def search_mortalites(self, query, actif_only: bool = True):
        return self.repository.search_mortalites(query, actif_only=actif_only)

    def update_deces(self, deces, **data):
        return self.repository.update_deces(deces, **data)

    def delete_deces(self, deces_or_id, hard=False):
        return self.repository.delete_deces(deces_or_id, hard=hard)

