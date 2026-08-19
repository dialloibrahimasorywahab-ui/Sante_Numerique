from .models import Service


class ServiceRepository:

    # Création d'un service
    def createService(self, **data):
        return Service.objects.create(**data)

    # Obtenir un service par son ID
    def get_service(self, service_id):
        try:
            return Service.objects.get(idService=service_id)
        except Service.DoesNotExist:
            return None

    # Obtenir un service par son nom
    def get_service_by_nom(self, nom_service):
        try:
            return Service.objects.get(nomService__iexact=nom_service)
        except Service.DoesNotExist:
            return None

    # Récupérer tous les services
    def get_all_services(self):
        return Service.objects.all()

    # Mettre à jour les données d'un service
    def update_service(self, service, **data):
        for field, value in data.items():
            setattr(service, field, value)
        service.save()
        return service

    # Supprimer un service
    def delete_service(self, service):
        service.delete()
