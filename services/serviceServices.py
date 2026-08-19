from .models import Service
from .serviceRepositories import ServiceRepository


class ServiceService:

    def __init__(self):
        self.repository = ServiceRepository()

    # Création d'un service
    def createService(self, **data):
        return self.repository.createService(**data)

    # Récupérer un service par son ID
    def get_service(self, service_id):
        return self.repository.get_service(service_id)

    # Récupérer ou créer un service par son nom
    def get_or_create_service_by_nom(self, nom_service):
        if not nom_service:
            return None
        service = self.repository.get_service_by_nom(nom_service)
        if service:
            return service
        
        # Correspondance avec le dictionnaire NomService
        valid_choices = {choice[0]: choice[0] for choice in Service.NomService.choices}
        matched_choice = valid_choices.get(str(nom_service).upper(), Service.NomService.MEDECINE_GENERALE)
        
        try:
            return self.repository.createService(nomService=matched_choice)
        except Exception:
            return self.repository.get_service_by_nom(matched_choice)

    # Récupérer tous les services
    def get_all_services(self):
        return self.repository.get_all_services()

    # Mettre à jour un service
    def update_service(self, service, **data):
        return self.repository.update_service(service, **data)

    # Supprimer un service
    def delete_service(self, service):
        return self.repository.delete_service(service)

    # Initialisation de tous les services du dictionnaire s'ils n'existent pas
    def seed_default_services(self):
        created_services = []
        for choice_key, choice_label in Service.NomService.choices:
            service, _ = Service.objects.get_or_create(
                nomService=choice_key,
                defaults={"description": f"Service de {choice_label}"}
            )
            created_services.append(service)
        return created_services
