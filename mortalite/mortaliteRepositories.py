from django.db.models import Q
from .models import Mortalite


class MortaliteRepository:
    def createDeces(self, **data):
        return Mortalite.objects.create(**data)

    def get_DecesById(self, deces_id):
        try:
            return Mortalite.objects.select_related(
                'id_patient__idUtilisateur',
                'id_medecin__idUtilisateur'
            ).get(pk=deces_id)
        except Mortalite.DoesNotExist:
            return None

    def get_all_mortalites(self):
        return Mortalite.objects.select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        ).all()

    def get_mortalites_by_patient(self, patient_id):
        return Mortalite.objects.filter(id_patient_id=patient_id).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )

    def get_mortalites_by_medecin(self, medecin_id):
        return Mortalite.objects.filter(id_medecin_id=medecin_id).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )

    def get_mortalites_by_date(self, date_deces):
        return Mortalite.objects.filter(date_deces=date_deces).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )

    def search_mortalites(self, query):
        if not query:
            return self.get_all_mortalites()
        return Mortalite.objects.filter(
            Q(cause_deces__icontains=query) |
            Q(lieu_deces__icontains=query) |
            Q(observation__icontains=query) |
            Q(id_patient__idUtilisateur__nom__icontains=query) |
            Q(id_patient__idUtilisateur__prenom__icontains=query)
        ).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )

    def update_deces(self, deces, **data):
        for field, value in data.items():
            setattr(deces, field, value)
        deces.save()
        return deces

    def delete_deces(self, deces_or_id, hard=False):
        instance = deces_or_id if isinstance(deces_or_id, Mortalite) else self.get_DecesById(deces_or_id)
        if instance:
            if hard:
                instance.delete()
            else:
                instance.actif = False
                instance.save()
            return True
        return False

