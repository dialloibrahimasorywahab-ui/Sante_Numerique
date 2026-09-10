from common.services import BaseService
from .models import Service
from .serviceRepositories import ServiceRepository


class ServiceService(BaseService[Service]):

    def __init__(self):
        self.repository = ServiceRepository()
        super().__init__(repository=self.repository)

    def createService(self, **data):
        return self.repository.createService(**data)

    def get_service(self, service_id):
        return self.repository.get_service(service_id)

    def get_or_create_service_by_nom(self, nom_service):
        if not nom_service:
            return None
        service = self.repository.get_service_by_nom(nom_service)
        if service:
            return service

        valid_choices = {choice[0]: choice[0] for choice in Service.NomService.choices}
        matched_choice = valid_choices.get(str(nom_service).upper(), Service.NomService.MEDECINE_GENERALE)

        try:
            return self.repository.createService(nom_service=matched_choice)
        except Exception:
            return self.repository.get_service_by_nom(matched_choice)

    def get_all_services(self, actif_only: bool = True):
        return self.repository.get_all_services(actif_only=actif_only)

    def search_services(self, query, actif_only: bool = True):
        return self.repository.search_services(query, actif_only=actif_only)

    def update_service(self, service, **data):
        return self.repository.update_service(service, **data)

    def delete_service(self, service, hard=False):
        return self.repository.delete_service(service, hard=hard)

    def seed_default_services(self):
        created_services = []
        for choice_key, choice_label in Service.NomService.choices:
            service, _ = Service.objects.get_or_create(
                nom_service=choice_key,
                defaults={"description": f"Service de {choice_label}"}
            )
            created_services.append(service)
        return created_services
