# pyrefly: ignore [missing-import]
import random
# pyrefly: ignore [missing-import]
from django.db import transaction
# pyrefly: ignore [missing-import]
from django.utils import timezone
from users.models import User
from users.usersServices import UserService
from .personnelRepositories import PersonnelRepository


class PersonnelService:

    # Instanciation des services et repositories
    def __init__(self):
        self.repository = PersonnelRepository()
        self.user_service = UserService()
        from services.serviceServices import ServiceService
        self.service_service = ServiceService()

    # Enregistrement d'un membre du personnel (prend en charge la création combinée User + Personnel)
    def createPersonnel(self, **data):
        id_user_data = data.pop("idUtilisateur", None)

        def resolve_role(provided_role, type_personnel):
            if provided_role in User.Role.values:
                return provided_role
            if type_personnel in ["ADMINISTRATIF", "ADMINISTRATEUR"]:
                return User.Role.ADMINISTRATEUR
            return User.Role.INFIRMIER

        def build_user_payload(u_info):
            prenom = u_info.get("prenom", "") or data.pop("prenom", "")
            nom = u_info.get("nom", "") or data.pop("nom", "")
            login = data.pop("login", None) or u_info.get("login")
            if not login:
                clean_p = prenom.lower().replace(" ", "") if prenom else "staff"
                clean_n = nom.lower().replace(" ", "") if nom else "soignant"
                login = f"staff_{clean_p}_{clean_n}_{random.randint(100, 999)}"
            email = u_info.get("email") or data.pop("email", None) or data.get("emailPro") or f"{login}@santenumerique.com"
            telephone = u_info.get("telephone") or data.pop("telephone", None) or data.get("telephonePro") or f"+22462{random.randint(1000000, 9999999)}"
            password = data.pop("motDePasse", "PersonnelPass123!")
            role_user = resolve_role(u_info.get("role") or data.get("role"), data.get("typePersonnel"))

            return {
                "nom": nom or "Personnel",
                "prenom": prenom or "Soignant",
                "email": email,
                "telephone": telephone,
                "dateNaissance": u_info.get("dateNaissance") or data.pop("dateNaissance", None),
                "login": login,
                "motDePasseHash": password,
                "role": role_user,
                "actif": True,
            }

        if isinstance(id_user_data, User):
            user = id_user_data
        elif isinstance(id_user_data, dict):
            user_payload = build_user_payload(id_user_data)
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)
        else:
            user_payload = build_user_payload({})
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)

        # Nettoyage des champs virtuels
        data.pop("login", None)
        data.pop("motDePasse", None)
        data.pop("email", None)
        data.pop("telephone", None)

        if user:
            data["idUtilisateur"] = user
            if not data.get("emailPro"):
                data["emailPro"] = user.email
            if not data.get("telephonePro"):
                data["telephonePro"] = user.telephone

        if "dateEmbauche" not in data or not data["dateEmbauche"]:
            data["dateEmbauche"] = timezone.now().date()

        # Résolution et rattachement automatique de idService
        service_input = data.get("idService") or data.get("serviceHopital")
        if service_input:
            if isinstance(service_input, int):
                service_obj = self.service_service.get_service(service_input)
            elif isinstance(service_input, str):
                service_obj = self.service_service.get_or_create_service_by_nom(service_input)
            else:
                service_obj = service_input
            if service_obj:
                data["idService"] = service_obj
                data["serviceHopital"] = service_obj.get_nomService_display()

        return self.repository.createPersonnel(**data)

    # Rechercher et afficher un membre du personnel par son ID
    def get_Personnel(self, personnel_id):
        return self.repository.get_personnel(personnel_id)

    # Récupérer tout le personnel
    def get_all_personnel(self):
        return self.repository.get_all_personnel()

    # Récupérer le personnel par type
    def get_personnel_by_type(self, type_personnel):
        return self.repository.get_personnel_by_type(type_personnel)

    # Mettre à jour les données d'un membre du personnel
    def update_personnel(self, personnel, **data):
        id_user_data = data.pop("idUtilisateur", None)
        user_updates = {}

        if isinstance(id_user_data, dict):
            user_updates.update(id_user_data)
        elif isinstance(id_user_data, User):
            personnel.idUtilisateur = id_user_data

        for key in ["nom", "prenom", "email", "telephone", "dateNaissance", "login", "motDePasse", "motDePasseHash"]:
            if key in data:
                user_updates[key] = data.pop(key)

        data.pop("login", None)
        data.pop("motDePasse", None)

        service_input = data.get("idService") or data.get("serviceHopital")
        if service_input:
            if isinstance(service_input, int):
                service_obj = self.service_service.get_service(service_input)
            elif isinstance(service_input, str):
                service_obj = self.service_service.get_or_create_service_by_nom(service_input)
            else:
                service_obj = service_input
            if service_obj:
                data["idService"] = service_obj
                data["serviceHopital"] = service_obj.get_nomService_display()

        with transaction.atomic():
            if user_updates and personnel.idUtilisateur:
                self.user_service.updateUser(personnel.idUtilisateur, **user_updates)
            return self.repository.update_Personnel(personnel, **data)

    # Désactiver ou supprimer un membre du personnel
    def delete_personnel(self, personnel, hard=False):
        return self.repository.delete_personnel(personnel, hard=hard)

