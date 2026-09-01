from .models import Chambre


class ChambreRepository:

    def create_chambre(self, **data):
        return Chambre.objects.create(**data)

    def get_chambre(self, chambre_id):
        try:
            return Chambre.objects.select_related('batiment').get(id=chambre_id)
        except Chambre.DoesNotExist:
            return None

    def get_all_chambres(self, actif_only: bool = True):
        qs = Chambre.objects.select_related('batiment').all()
        if actif_only:
            qs = qs.exclude(statut=Chambre.StatutChambre.HORS_SERVICE)
        return qs

    def get_chambres_by_batiment(self, batiment_id, actif_only: bool = True):
        qs = Chambre.objects.filter(batiment_id=batiment_id).select_related('batiment')
        if actif_only:
            qs = qs.exclude(statut=Chambre.StatutChambre.HORS_SERVICE)
        return qs

    def get_chambres_by_type(self, type_chambre, actif_only: bool = True):
        qs = Chambre.objects.select_related('batiment').all()
        if type_chambre:
            clean_type = str(type_chambre).strip().upper()
            qs = qs.filter(type_chambre__iexact=clean_type)
        if actif_only:
            qs = qs.exclude(statut=Chambre.StatutChambre.HORS_SERVICE)
        return qs

    def get_chambres_by_statut(self, statut, actif_only: bool = True):
        qs = Chambre.objects.select_related('batiment').all()
        if statut:
            clean_statut = str(statut).strip().upper()
            qs = qs.filter(statut__iexact=clean_statut)
        elif actif_only:
            qs = qs.exclude(statut=Chambre.StatutChambre.HORS_SERVICE)
        return qs


    def search_chambres(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_chambres(actif_only=actif_only)
        clean_q = str(query).strip()
        if clean_q.isdigit():
            qs = Chambre.objects.filter(numero_chambre=int(clean_q)).select_related('batiment')
        else:
            qs = Chambre.objects.filter(batiment__nom__icontains=clean_q).select_related('batiment')
        if actif_only:
            qs = qs.exclude(statut=Chambre.StatutChambre.HORS_SERVICE)
        return qs


    def update_chambre(self, chambre, **data):
        for field, value in data.items():
            setattr(chambre, field, value)
        chambre.save()
        return chambre

    def delete_chambre(self, chambre, hard=False):
        if hard:
            chambre.delete()
        else:
            chambre.statut = Chambre.StatutChambre.HORS_SERVICE
            chambre.save()


