from django.db import models
from common.repositories import BaseRepository
from .models import Lit


class LitRepository(BaseRepository[Lit]):

    def __init__(self):
        super().__init__(model=Lit)

    def create_lit(self, **data):
        return self.create(**data)

    def get_lit(self, lit_id):
        return self.get_by_id(lit_id, select_related=['chambre', 'chambre__batiment'])

    def get_all_lits(self, actif_only: bool = True):
        qs = self.model.objects.select_related('chambre', 'chambre__batiment').all()
        if actif_only:
            qs = qs.exclude(etat=Lit.EtatLit.HORS_SERVICE)
        return qs

    def get_lits_by_chambre(self, chambre_id, actif_only: bool = True):
        qs = self.model.objects.filter(chambre_id=chambre_id).select_related('chambre', 'chambre__batiment')
        if actif_only:
            qs = qs.exclude(etat=Lit.EtatLit.HORS_SERVICE)
        return qs

    def get_lits_by_etat(self, etat, actif_only: bool = True):
        qs = self.model.objects.select_related('chambre', 'chambre__batiment').all()
        if etat:
            qs = qs.filter(etat=etat)
        elif actif_only:
            qs = qs.exclude(etat=Lit.EtatLit.HORS_SERVICE)
        return qs

    def search_lits(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_lits(actif_only=actif_only)
        q_clean = str(query).strip()
        qs = self.model.objects.filter(
            models.Q(numero_lit__icontains=q_clean) |
            models.Q(etat__icontains=q_clean) |
            models.Q(chambre__batiment__nom__icontains=q_clean)
        ).select_related('chambre', 'chambre__batiment')
        if actif_only:
            qs = qs.exclude(etat=Lit.EtatLit.HORS_SERVICE)
        return qs

    def update_lit(self, lit, **data):
        return self.update(lit, **data)

    def delete_lit(self, lit, hard=False):
        if hard:
            return self.delete(lit, hard=True)
        else:
            lit.etat = Lit.EtatLit.HORS_SERVICE
            lit.save(update_fields=['etat'])
            return True
