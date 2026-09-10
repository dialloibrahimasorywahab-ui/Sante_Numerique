from django.db.models import Q
from common.repositories import BaseRepository
from .models import Medecin


class MedecinRepository(BaseRepository[Medecin]):
    """
    Repository pour l'accès aux données des médecins.
    Hérite des méthodes CRUD génériques de BaseRepository.
    """
    def __init__(self):
        super().__init__(model=Medecin)

    def createMedecin(self, **data):
        return self.create(**data)

    def get_medecin(self, medecin_id):
        return self.get_by_id(medecin_id, select_related=['id_utilisateur'])

    def get_all_medecin(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only, select_related=['id_utilisateur'])

    def get_medecins_by_specialite(self, specialite, actif_only: bool = True):
        spec_clean = str(specialite).strip().upper()

        spec_list = [spec_clean]
        if spec_clean in ["MEDECINE_GENERALE", "GENERALISTE", "URGENCES"]:
            spec_list = ["GENERALISTE", "MEDECINE_GENERALE"]
        elif spec_clean in ["GYNECOLOGIE", "MATERNITE"]:
            spec_list = ["GYNECOLOGIE", "MATERNITE"]
        elif spec_clean in ["CHIRURGIE", "CHIRURGIE_GENERALE"]:
            spec_list = ["CHIRURGIE", "CHIRURGIE_GENERALE"]

        q_filter = Q()
        for s in spec_list:
            q_filter |= Q(specialite__iexact=s)

        qs = self.model.objects.filter(q_filter).select_related('id_utilisateur')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    def search_medecins(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=[
                'id_utilisateur__nom',
                'id_utilisateur__prenom',
                'id_utilisateur__email',
                'matricule',
                'specialite'
            ],
            actif_only=actif_only,
            select_related=['id_utilisateur']
        )

    def update_Medecin(self, medecin, **data):
        return self.update(medecin, **data)

    def delete_medecin(self, medecin, hard=False):
        return self.delete(medecin, hard=hard)
