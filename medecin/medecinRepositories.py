from .models import Medecin


class MedecinRepository:

    # Enregistrement d'un médecin
    def createMedecin(self, **data):
        return Medecin.objects.create(**data)

    # Rechercher et afficher un médecin par son ID
    def get_medecin(self, medecin_id):
        try:
            return Medecin.objects.get(idMedecin=medecin_id)
        except Medecin.DoesNotExist:
            return None

    # Afficher tous les médecins
    def get_all_medecin(self):
        return Medecin.objects.all()

    # Rechercher les médecins par spécialité / service
    def get_medecins_by_specialite(self, specialite):
        return Medecin.objects.filter(specialite__iexact=specialite)

    # Mettre à jour les informations d'un médecin
    def update_Medecin(self, medecin, **data):
        for field, value in data.items():
            setattr(medecin, field, value)
        medecin.save()
        return medecin

    # Désactiver ou supprimer un médecin
    def delete_medecin(self, medecin, hard=False):
        if hard:
            if medecin.idUtilisateur:
                medecin.idUtilisateur.delete()
            else:
                medecin.delete()
        else:
            if medecin.idUtilisateur:
                medecin.idUtilisateur.actif = False
                medecin.idUtilisateur.save()

