from .models import Personnel


class PersonnelRepository:

    # Enregistrement d'un membre du personnel
    def createPersonnel(self, **data):
        return Personnel.objects.create(**data)

    # Rechercher et afficher un membre du personnel par son ID
    def get_personnel(self, personnel_id):
        try:
            return Personnel.objects.select_related('idUtilisateur', 'idService').get(idPersonnel=personnel_id)
        except Personnel.DoesNotExist:
            return None

    # Afficher tout le personnel
    def get_all_personnel(self):
        return Personnel.objects.select_related('idUtilisateur', 'idService').all()

    # Rechercher le personnel par type (ex: INFIRMIER, ADMINISTRATIF)
    def get_personnel_by_type(self, type_personnel):
        return Personnel.objects.filter(typePersonnel__iexact=type_personnel).select_related('idUtilisateur', 'idService')

    # Rechercher le personnel par service
    def get_personnel_by_service(self, service_id):
        return Personnel.objects.filter(idService_id=service_id).select_related('idUtilisateur', 'idService')

    # Rechercher des membres du personnel par mot-clé
    def search_personnel(self, query):
        if not query:
            return self.get_all_personnel()
        from django.db.models import Q
        clean_q = str(query).strip()
        return Personnel.objects.filter(
            Q(idUtilisateur__nom__icontains=clean_q) |
            Q(idUtilisateur__prenom__icontains=clean_q) |
            Q(idUtilisateur__email__icontains=clean_q) |
            Q(matricule__icontains=clean_q) |
            Q(typePersonnel__icontains=clean_q)
        ).select_related('idUtilisateur', 'idService')

    # Mettre à jour les informations d'un membre du personnel
    def update_Personnel(self, personnel, **data):
        for field, value in data.items():
            setattr(personnel, field, value)
        personnel.save()
        return personnel

    # Désactiver ou supprimer un membre du personnel
    def delete_personnel(self, personnel, hard=False):
        if hard:
            if personnel.idUtilisateur:
                personnel.idUtilisateur.delete()
            else:
                personnel.delete()
        else:
            if personnel.idUtilisateur:
                personnel.idUtilisateur.actif = False
                personnel.idUtilisateur.save()

