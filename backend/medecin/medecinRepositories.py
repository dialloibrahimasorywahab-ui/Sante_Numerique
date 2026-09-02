from .models import Medecin


class MedecinRepository:

    # Enregistrement d'un médecin
    def createMedecin(self, **data):
        return Medecin.objects.create(**data)

    # Rechercher et afficher un médecin par son ID
    def get_medecin(self, medecin_id):
        try:
            return Medecin.objects.select_related('id_utilisateur').get(id_medecin=medecin_id)
        except Medecin.DoesNotExist:
            return None

    # Afficher tous les médecins
    def get_all_medecin(self, actif_only: bool = True):
        qs = Medecin.objects.select_related('id_utilisateur').all()
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    # Rechercher les médecins par spécialité / service
    def get_medecins_by_specialite(self, specialite, actif_only: bool = True):
        qs = Medecin.objects.filter(specialite__iexact=specialite).select_related('id_utilisateur')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    # Rechercher des médecins par mot-clé
    def search_medecins(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_medecin(actif_only=actif_only)
        from django.db.models import Q
        clean_q = str(query).strip()
        qs = Medecin.objects.filter(
            Q(id_utilisateur__nom__icontains=clean_q) |
            Q(id_utilisateur__prenom__icontains=clean_q) |
            Q(id_utilisateur__email__icontains=clean_q) |
            Q(matricule__icontains=clean_q) |
            Q(specialite__icontains=clean_q)
        ).select_related('id_utilisateur')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    # Mettre à jour les informations d'un médecin
    def update_Medecin(self, medecin, **data):
        for field, value in data.items():
            setattr(medecin, field, value)
        medecin.save()
        return medecin

    # Désactiver ou supprimer un médecin
    def delete_medecin(self, medecin, hard=False):
        if hard:
            if medecin.id_utilisateur:
                medecin.id_utilisateur.delete()
            else:
                medecin.delete()
        else:
            if medecin.id_utilisateur:
                medecin.id_utilisateur.actif = False
                medecin.id_utilisateur.save(update_fields=["actif"])
        return medecin
