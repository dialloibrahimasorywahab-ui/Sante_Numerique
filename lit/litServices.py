from .litRepositories import LitRepository
from .models import Lit


class LitService:

    def __init__(self):
        self.repository = LitRepository()

    def create_lit(self, **data):
        lit = self.repository.create_lit(**data)
        if lit.chambre:
            lit.chambre.sync_statut()
        return lit

    def get_lit(self, lit_id):
        return self.repository.get_lit(lit_id)

    def get_all_lits(self):
        return self.repository.get_all_lits()

    def get_lits_by_chambre(self, chambre_id):
        return self.repository.get_lits_by_chambre(chambre_id)

    def get_lits_by_etat(self, etat):
        return self.repository.get_lits_by_etat(etat)

    def search_lits(self, query):
        return self.repository.search_lits(query)

    def update_lit(self, lit, **data):
        updated_lit = self.repository.update_lit(lit, **data)
        if updated_lit.chambre:
            updated_lit.chambre.sync_statut()
        return updated_lit

    def delete_lit(self, lit):
        chambre = lit.chambre
        res = self.repository.delete_lit(lit)
        if chambre:
            chambre.sync_statut()
        return res


    def generate_lits_pour_chambre(self, chambre):
        """Génère automatiquement les lits d'une chambre selon sa capacité (nombre de lits)."""
        lits_crees = []
        lits_existants = list(chambre.lits.all())
        nb_actuel = len(lits_existants)
        capacite = chambre.capacite

        if nb_actuel < capacite:
            for i in range(nb_actuel + 1, capacite + 1):
                numero_lit = f"Lit {i}"
                lit = self.create_lit(
                    chambre=chambre,
                    numero_lit=numero_lit,
                    etat=Lit.EtatLit.DISPONIBLE
                )
                lits_crees.append(lit)
        return lits_crees
