from .chambreRepositories import ChambreRepository


class ChambreService:

    def __init__(self):
        self.repository = ChambreRepository()

    def create_chambre(self, **data):
        return self.repository.create_chambre(**data)

    def get_chambre(self, chambre_id):
        return self.repository.get_chambre(chambre_id)

    def get_all_chambres(self):
        return self.repository.get_all_chambres()

    def get_chambres_by_batiment(self, batiment_id):
        return self.repository.get_chambres_by_batiment(batiment_id)

    def get_chambres_by_type(self, type_chambre):
        return self.repository.get_chambres_by_type(type_chambre)

    def get_chambres_by_statut(self, statut):
        return self.repository.get_chambres_by_statut(statut)

    def search_chambres(self, query):
        return self.repository.search_chambres(query)

    def sync_statut_chambre(self, chambre_id):
        chambre = self.get_chambre(chambre_id)
        if chambre:
            return chambre.sync_statut()
        return None



    def update_chambre(self, chambre, **data):
        return self.repository.update_chambre(chambre, **data)

    def delete_chambre(self, chambre):
        return self.repository.delete_chambre(chambre)

