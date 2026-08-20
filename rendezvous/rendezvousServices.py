# pyrefly: ignore [missing-import]
from .rendezvousRepositories import RendezVousRepository


class RendezVousService:

    def __init__(self):
        self.repository = RendezVousRepository()

    def create_rendezvous(self, **data):
        return self.repository.create_rendezvous(**data)

    def get_rendezvous(self, rdv_id):
        return self.repository.get_rendezvous(rdv_id)

    def get_all_rendezvous(self):
        return self.repository.get_all_rendezvous()

    def get_rendezvous_by_patient(self, patient_id):
        return self.repository.get_rendezvous_by_patient(patient_id)

    def get_rendezvous_by_medecin(self, medecin_id):
        return self.repository.get_rendezvous_by_medecin(medecin_id)

    def get_rendezvous_by_statut(self, statut):
        return self.repository.get_rendezvous_by_statut(statut)

    def get_rendezvous_by_date(self, date_rdv):
        return self.repository.get_rendezvous_by_date(date_rdv)

    def search_rendezvous(self, query):
        return self.repository.search_rendezvous(query)

    def update_rendezvous(self, rdv, **data):
        return self.repository.update_rendezvous(rdv, **data)

    def delete_rendezvous(self, rdv):
        return self.repository.delete_rendezvous(rdv)
