from .nataliteRepositories import NataliteRepository


class NataliteService:
    def __init__(self):
        self.repository = NataliteRepository()
    
    # Enregistrement d'un nouveau-né
    def create_nouveaune(self, **data):
        return self.repository.createNouveauNe(**data)
    
    # Rechercher un nouveau-né par son id
    def get_nouveauneById(self, nouveau_ne_id):
        return self.repository.get_NouveauNeById(nouveau_ne_id)

    # Récupérer tous les nouveaux-nés
    def get_all_nouveau_ne(self):
        return self.repository.get_all_nouveaux_nes()
    
    # Afficher les nouveaux-nés d'une patiente (mère)
    def get_nouveaux_nes_by_patient(self, patient_id):
        return self.repository.get_nouveaux_nes_by_patient(patient_id)

    # Afficher les nouveaux-nés sous la supervision d'un médecin
    def get_nouveaux_nes_by_medecin(self, medecin_id):
        return self.repository.get_nouveaux_nes_by_medecin(medecin_id)

    # Afficher les nouveaux-nés par leur sexe
    def get_natalities_by_sexe(self, sexe):
        return self.repository.get_natalities_by_sexe(sexe)

    # Afficher les nouveaux-nés d'une date
    def get_nouveaux_nes_by_date(self, date_naissance):
        return self.repository.get_nouveaux_nes_by_date(date_naissance)

    # Recherche
    def search_nouveaux_nes(self, query):
        return self.repository.search_nouveaux_nes(query)

    # Mettre à jour les informations d'un nouveau-né
    def update_data_nouveau_ne(self, nouveau_ne, **data):
        return self.repository.update_data_nouveau_ne(nouveau_ne, **data)
    
    # Supprimer une natalité
    def delete_nouveau_ne(self, nouveau_ne_or_id):
        return self.repository.delete_nouveau_ne(nouveau_ne_or_id)