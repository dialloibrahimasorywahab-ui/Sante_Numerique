from .nataliteRepositories import NataliteRepository


class NataliteService:
    # instanciation du repository pour avoir accèes à ces données
    def __init__(self):
        self.repository = NataliteRepository()
    
    # Enregistrement d'un nouveau-né
    def create_nouveaune(self, **data):
        return self.repository.createNouveauNe(**data)
    
    # Rechercher un nouveau-né par son id
    def get_nouveauneById(self, nouveau_ne_id):
        return self.repository.get_NouveauNeById(nouveau_ne_id)

    # Récupérer tous les nouveaux-nés
    def get_all_nouveau_ne(self, actif_only: bool = True):
        return self.repository.get_all_nouveaux_nes(actif_only=actif_only)
    
    # Afficher les nouveaux-nés d'une patiente (mère)
    def get_nouveaux_nes_by_patient(self, patient_id, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_patient(patient_id, actif_only=actif_only)

    # Afficher les nouveaux-nés sous la supervision d'un médecin
    def get_nouveaux_nes_by_medecin(self, medecin_id, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_medecin(medecin_id, actif_only=actif_only)

    # Afficher les nouveaux-nés par leur sexe
    def get_natalities_by_sexe(self, sexe, actif_only: bool = True):
        return self.repository.get_natalities_by_sexe(sexe, actif_only=actif_only)

    # Afficher les nouveaux-nés d'une date
    def get_nouveaux_nes_by_date(self, date_naissance, actif_only: bool = True):
        return self.repository.get_nouveaux_nes_by_date(date_naissance, actif_only=actif_only)

    # Recherche
    def search_nouveaux_nes(self, query, actif_only: bool = True):
        return self.repository.search_nouveaux_nes(query, actif_only=actif_only)

    # Mettre à jour les informations d'un nouveau-né
    def update_data_nouveau_ne(self, nouveau_ne, **data):
        return self.repository.update_data_nouveau_ne(nouveau_ne, **data)
    
    # Désactiver ou supprimer une natalité
    def delete_nouveau_ne(self, nouveau_ne_or_id, hard=False):
        return self.repository.delete_nouveau_ne(nouveau_ne_or_id, hard=hard)