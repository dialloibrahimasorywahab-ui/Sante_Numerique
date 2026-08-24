# pyrefly: ignore [missing-import]
from .rendezvousRepositories import RendezVousRepository


class RendezVousService:
    # initialisation du repository pour avoir accès à ces données
    def __init__(self):
        self.repository = RendezVousRepository()

    # creation d'un rendez-vous 

    def create_rendezvous(self, **data):
        return self.repository.create_rendezvous(**data)

    # rechercher un rendez-vous par son id

    def get_rendezvous(self, rdv_id):
        return self.repository.get_rendezvous(rdv_id)

    #  afficher tous les rendez-vous

    def get_all_rendezvous(self):
        return self.repository.get_all_rendezvous()

    # afficher le rendez-vous d'un patient 

    def get_rendezvous_by_patient(self, patient_id):
        return self.repository.get_rendezvous_by_patient(patient_id)

    #  afficher les rendez-vous d'un medecin 

    def get_rendezvous_by_medecin(self, medecin_id):
        return self.repository.get_rendezvous_by_medecin(medecin_id)

    # afficher les statuts des différents rendez-vous 

    def get_rendezvous_by_statut(self, statut):
        return self.repository.get_rendezvous_by_statut(statut)

    # afficher les rendez-vous d'une date 

    def get_rendezvous_by_date(self, date_rdv):
        return self.repository.get_rendezvous_by_date(date_rdv)

    # rechercher un rendez-vous

    def search_rendezvous(self, query):
        return self.repository.search_rendezvous(query)

    # mettre a jour les informations d'un rendez-vous 

    def update_rendezvous(self, rdv, **data):
        return self.repository.update_rendezvous(rdv, **data)

    # Annuler un rendez-vous

    def delete_rendezvous(self, rdv):
        return self.repository.delete_rendezvous(rdv)
