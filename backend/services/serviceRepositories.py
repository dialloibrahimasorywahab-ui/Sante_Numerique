from .models import Service


class ServiceRepository:

    # Création d'un service
    def createService(self, **data):
        return Service.objects.create(**data)

    # Obtenir un service par son ID
    def get_service(self, service_id):
        try:
            return Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return None

    # Obtenir un service par son nom
    def get_service_by_nom(self, nom_service):
        try:
            return Service.objects.get(nom_service__iexact=nom_service)
        except Service.DoesNotExist:
            return None

    # Récupérer tous les services
    def get_all_services(self, actif_only: bool = True):
        qs = Service.objects.all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Rechercher des services par mot-clé
    def search_services(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_services(actif_only=actif_only)
        from django.db.models import Q
        clean_q = str(query).strip()
        qs = Service.objects.filter(
            Q(nom_service__icontains=clean_q) | Q(description__icontains=clean_q)
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    # Mettre à jour les données d'un service
    def update_service(self, service, **data):
        for field, value in data.items():
            setattr(service, field, value)
        service.save()
        return service

    # Désactiver ou supprimer un service
    def delete_service(self, service, hard=False):
        if hard:
            service.delete()
        else:
            service.actif = False
            service.save()

