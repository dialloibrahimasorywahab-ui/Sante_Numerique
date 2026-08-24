# pyrefly: ignore [missing-import]
from django.db.models import Q
from .models import Batiment


class BatimentRepository:

    def create_batiment(self, **data):
        return Batiment.objects.create(**data)

    def get_batiment(self, batiment_id):
        try:
            return Batiment.objects.get(idBatiment=batiment_id)
        except Batiment.DoesNotExist:
            return None

    def get_batiment_by_nom(self, nom):
        if not nom:
            return None
        try:
            return Batiment.objects.get(nom__iexact=nom.strip())
        except Batiment.DoesNotExist:
            return None

    def get_all_batiments(self):
        return Batiment.objects.all()

    def search_batiments(self, query):
        if not query:
            return self.get_all_batiments()
        clean_query = query.strip()
        return Batiment.objects.filter(
            Q(nom__icontains=clean_query) | Q(description__icontains=clean_query)
        )

    def update_batiment(self, batiment, **data):
        for field, value in data.items():
            setattr(batiment, field, value)
        batiment.save()
        return batiment

    def delete_batiment(self, batiment, hard=False):
        if hard:
            batiment.delete()
        else:
            batiment.actif = False
            batiment.save()


