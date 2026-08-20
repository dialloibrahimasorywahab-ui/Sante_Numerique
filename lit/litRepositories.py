# pyrefly: ignore [missing-import]
from django.db import models
from .models import Lit


class LitRepository:

    def create_lit(self, **data):
        return Lit.objects.create(**data)

    def get_lit(self, lit_id):
        try:
            return Lit.objects.select_related('chambre', 'chambre__batiment').get(id=lit_id)
        except Lit.DoesNotExist:
            return None

    def get_all_lits(self):
        return Lit.objects.select_related('chambre', 'chambre__batiment').all()

    def get_lits_by_chambre(self, chambre_id):
        return Lit.objects.filter(chambre_id=chambre_id).select_related('chambre', 'chambre__batiment')

    def get_lits_by_etat(self, etat):
        return Lit.objects.filter(etat=etat).select_related('chambre', 'chambre__batiment')

    def search_lits(self, query):
        if not query:
            return self.get_all_lits()
        q_clean = str(query).strip()
        return Lit.objects.filter(
            models.Q(numero_lit__icontains=q_clean) |
            models.Q(etat__icontains=q_clean) |
            models.Q(chambre__batiment__nom__icontains=q_clean)
        ).select_related('chambre', 'chambre__batiment')

    def update_lit(self, lit, **data):
        for field, value in data.items():
            setattr(lit, field, value)
        lit.save()
        return lit

    def delete_lit(self, lit):
        lit.delete()
