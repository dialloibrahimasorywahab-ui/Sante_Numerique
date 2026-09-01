from django.db.models import Q
from .models import Natalite


class NataliteRepository:
    
    # Enregistrement d'un nouveau-né
    def createNouveauNe(self, **data):
        return Natalite.objects.create(**data)

    # Rechercher et afficher un nouveau-né par son id
    def get_NouveauNeById(self, nouveauNe_id):
        try:
            return Natalite.objects.select_related(
                'id_patient__idUtilisateur',
                'id_medecin__idUtilisateur'
            ).get(pk=nouveauNe_id)
        except Natalite.DoesNotExist:
            return None

    # Afficher tous les nouveaux-nés
    def get_all_nouveaux_nes(self, actif_only: bool = True):
        qs = Natalite.objects.select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        ).all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Afficher les nouveaux-nés d'une patiente (mère)
    def get_nouveaux_nes_by_patient(self, patient_id, actif_only: bool = True):
        qs = Natalite.objects.filter(id_patient_id=patient_id).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Afficher les nouveaux-nés venus au monde sous la supervision d'un médecin
    def get_nouveaux_nes_by_medecin(self, medecin_id, actif_only: bool = True):
        qs = Natalite.objects.filter(id_medecin_id=medecin_id).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Afficher les nouveaux-nés par leur sexe
    def get_natalities_by_sexe(self, sexe, actif_only: bool = True):
        qs = Natalite.objects.filter(sexe=sexe).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Afficher les nouveaux-nés d'une date spécifique
    def get_nouveaux_nes_by_date(self, date_naissance, actif_only: bool = True):
        qs = Natalite.objects.filter(date_naissance=date_naissance).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Recherche textuelle
    def search_nouveaux_nes(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_nouveaux_nes(actif_only=actif_only)
        qs = Natalite.objects.filter(
            Q(prenom_nouveau_ne__icontains=query) |
            Q(nom_nouveau_ne__icontains=query) |
            Q(lieu_naissance__icontains=query) |
            Q(observation__icontains=query)
        ).select_related(
            'id_patient__idUtilisateur',
            'id_medecin__idUtilisateur'
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Mettre à jour les informations d'un nouveau-né
    def update_data_nouveau_ne(self, nouveau_ne, **data):
        for field, value in data.items():
            setattr(nouveau_ne, field, value)
        nouveau_ne.save()
        return nouveau_ne
    
    # Désactiver ou supprimer un nouveau-né par son id ou son instance
    def delete_nouveau_ne(self, nouveau_ne_or_id, hard=False):
        instance = nouveau_ne_or_id if isinstance(nouveau_ne_or_id, Natalite) else self.get_NouveauNeById(nouveau_ne_or_id)
        if instance:
            if hard:
                instance.delete()
            else:
                instance.actif = False
                instance.save()
            return True
        return False