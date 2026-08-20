from .models import Chambre


class ChambreRepository:

    def create_chambre(self, **data):
        return Chambre.objects.create(**data)

    def get_chambre(self, chambre_id):
        try:
            return Chambre.objects.select_related('batiment').get(id=chambre_id)
        except Chambre.DoesNotExist:
            return None

    def get_all_chambres(self):
        return Chambre.objects.select_related('batiment').all()

    def get_chambres_by_batiment(self, batiment_id):
        return Chambre.objects.filter(batiment_id=batiment_id).select_related('batiment')

    def get_chambres_by_type(self, type_chambre):
        if not type_chambre:
            return self.get_all_chambres()
        clean_type = str(type_chambre).strip().upper()
        return Chambre.objects.filter(type_chambre__iexact=clean_type).select_related('batiment')

    def get_chambres_by_statut(self, statut):
        if not statut:
            return self.get_all_chambres()
        clean_statut = str(statut).strip().upper()
        return Chambre.objects.filter(statut__iexact=clean_statut).select_related('batiment')


    def search_chambres(self, query):
        if not query:
            return self.get_all_chambres()
        clean_q = str(query).strip()
        if clean_q.isdigit():
            return Chambre.objects.filter(numero_chambre=int(clean_q)).select_related('batiment')
        return Chambre.objects.filter(batiment__nom__icontains=clean_q).select_related('batiment')


    def update_chambre(self, chambre, **data):
        for field, value in data.items():
            setattr(chambre, field, value)
        chambre.save()
        return chambre

    def delete_chambre(self, chambre):
        chambre.delete()

