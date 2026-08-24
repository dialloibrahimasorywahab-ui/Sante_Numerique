from django.db.models import Q
from .models import Mortalite


class MortaliteRepository:
    def createDeces(self, **data):
        return Mortalite.objects.create(**data)

    def get_DecesById(self, deces_id):
        try:
            return Mortalite.objects.get(pk=deces_id)
        except Mortalite.DoesNotExist:
            return None

    def get_all_mortalites(self):
        return Mortalite.objects.all()

    def get_mortalites_by_patient(self, patient_id):
        return Mortalite.objects.filter(id_patient_id=patient_id)

    def get_mortalites_by_medecin(self, medecin_id):
        return Mortalite.objects.filter(id_medecin_id=medecin_id)

    def get_mortalites_by_date(self, date_deces):
        return Mortalite.objects.filter(date_deces=date_deces)

    def search_mortalites(self, query):
        if not query:
            return self.get_all_mortalites()
        return Mortalite.objects.filter(
            Q(cause_deces__icontains=query) |
            Q(lieu_deces__icontains=query) |
            Q(observation__icontains=query) |
            Q(id_patient__idUtilisateur__nom__icontains=query) |
            Q(id_patient__idUtilisateur__prenom__icontains=query)
        )

    def update_deces(self, deces, **data):
        for field, value in data.items():
            setattr(deces, field, value)
        deces.save()
        return deces

    def delete_deces(self, deces_or_id):
        if isinstance(deces_or_id, Mortalite):
            deces_or_id.delete()
            return True
        else:
            instance = self.get_DecesById(deces_or_id)
            if instance:
                instance.delete()
                return True
        return False
