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

        # 1. Recherche directe par le nom exact / insensible à la casse
        service = self.repository.get_service_by_nom(nom_service)
        if service:
            return service

        nom_clean = str(nom_service).strip().lower()

        # 2. Correspondance exacte sur les clés ou libellés des choix
        for choice_key, choice_label in Service.NomService.choices:
            if nom_clean == choice_key.lower() or nom_clean == choice_label.lower():
                service = self.repository.get_service_by_nom(choice_key)
                if service:
                    return service
                return self.repository.createService(nom_service=choice_key, description=f"Service de {choice_label}")

        # 3. Correspondance partielle ou par mots-clés (ex: "général" -> MEDECINE_GENERALE)
        for choice_key, choice_label in Service.NomService.choices:
            if choice_key.lower() in nom_clean or choice_label.lower() in nom_clean:
                service = self.repository.get_service_by_nom(choice_key)
                if service:
                    return service
                return self.repository.createService(nom_service=choice_key, description=f"Service de {choice_label}")

        # 4. Fallback sur le service par défaut MEDECINE_GENERALE (vérifier s'il existe déjà !)
        fallback_choice = Service.NomService.MEDECINE_GENERALE
        service = self.repository.get_service_by_nom(fallback_choice)
        if service:
            return service

        # 5. Création sécurisée si le fallback n'existe pas en base
        service, _ = Service.objects.get_or_create(
            nom_service=fallback_choice,
            defaults={"description": "Service de Médecine Générale"}
        )
        return service

    def get_all_services(self, actif_only: bool = True):
        return self.repository.get_all_services(actif_only=actif_only)

    def search_services(self, query, actif_only: bool = True):
        return self.repository.search_services(query, actif_only=actif_only)

    def update_service(self, service, **data):
        return self.repository.update_service(service, **data)

    def delete_service(self, service_id, hard: bool = False):
        return self.repository.delete_service(service_id, hard=hard)
