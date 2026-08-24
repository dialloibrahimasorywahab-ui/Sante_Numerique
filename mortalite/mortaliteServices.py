from .mortaliteRepositories import MortaliteRepository


class MortaliteService:
    def __init__(self):
        self.repository = MortaliteRepository()

    def create_deces(self, **data):
        return self.repository.createDeces(**data)

    def get_deces_by_id(self, deces_id):
        return self.repository.get_DecesById(deces_id)

    def get_all_mortalites(self):
        return self.repository.get_all_mortalites()

    def get_mortalites_by_patient(self, patient_id):
        return self.repository.get_mortalites_by_patient(patient_id)

    def get_mortalites_by_medecin(self, medecin_id):
        return self.repository.get_mortalites_by_medecin(medecin_id)

    def get_mortalites_by_date(self, date_deces):
        return self.repository.get_mortalites_by_date(date_deces)

    def search_mortalites(self, query):
        return self.repository.search_mortalites(query)

    def update_deces(self, deces, **data):
        return self.repository.update_deces(deces, **data)

    def delete_deces(self, deces_or_id):
        return self.repository.delete_deces(deces_or_id)
