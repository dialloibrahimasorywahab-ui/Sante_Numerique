import random
import secrets
from django.db import transaction
from django.utils import timezone
from common.services import BaseService
from users.models import User
from users.usersServices import UserService
from .models import Personnel
from .personnelRepositories import PersonnelRepository


class PersonnelService(BaseService[Personnel]):
    """
    Service métier pour la gestion du personnel hospitalier et soignant.
    """
    def __init__(self):
        self.repository = PersonnelRepository()
        self.user_service = UserService()
        super().__init__(repository=self.repository)
        from services.serviceServices import ServiceService
        self.service_service = ServiceService()

    # Enregistrement d'un membre du personnel (prend en charge la création combinée User + Personnel)
    def createPersonnel(self, **data):
        id_user_data = data.pop("id_utilisateur", None) or data.pop("idUtilisateur", None)

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
            email = u_info.get("email") or data.pop("email", None) or data.get("emailPro") or data.get("email_pro") or f"{login}@santenumerique.com"
            telephone = u_info.get("telephone") or data.pop("telephone", None) or data.get("telephonePro") or data.get("telephone_pro") or f"+22462{random.randint(1000000, 9999999)}"
            password = data.pop("motDePasse", data.pop("mot_de_passe", None)) or secrets.token_urlsafe(16)
            role_user = resolve_role(u_info.get("role") or data.get("role") or data.get("type_personnel") or data.get("typePersonnel"), data.get("typePersonnel") or data.get("type_personnel"))

            return {
                "nom": nom or "Personnel",
                "prenom": prenom or "Soignant",
                "email": email,
                "telephone": telephone,
                "date_naissance": u_info.get("date_naissance") or u_info.get("dateNaissance") or data.pop("date_naissance", data.pop("dateNaissance", None)),
                "login": login,
                "mot_de_passe_hash": password,
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
        data.pop("mot_de_passe", None)
        data.pop("email", None)
        data.pop("telephone", None)

        if user:
            data["id_utilisateur"] = user
            if not data.get("emailPro") and not data.get("email_pro"):
                data["email_pro"] = user.email
            if not data.get("telephonePro") and not data.get("telephone_pro"):
                data["telephone_pro"] = user.telephone

        if "dateEmbauche" not in data and "date_embauche" not in data:
            data["date_embauche"] = timezone.now().date()

        # Résolution et rattachement automatique de idService
        service_input = data.pop("id_service", None) or data.pop("idService", None) or data.get("serviceHopital") or data.get("service_hopital")
        if service_input:
            if isinstance(service_input, int):
                service_obj = self.service_service.get_service(service_input)
            elif isinstance(service_input, str):
                service_obj = self.service_service.get_or_create_service_by_nom(service_input)
            else:
                service_obj = service_input
            if service_obj:
                data["id_service"] = service_obj
                data["service_hopital"] = service_obj.get_nom_service_display()

        return self.repository.createPersonnel(**data)

    # Rechercher et afficher un membre du personnel par son ID
    def get_Personnel(self, personnel_id):
        return self.repository.get_personnel(personnel_id)

    # Récupérer tout le personnel
    def get_all_personnel(self, actif_only: bool = True):
        return self.repository.get_all_personnel(actif_only=actif_only)

    # Récupérer le personnel par type
    def get_personnel_by_type(self, type_personnel, actif_only: bool = True):
        return self.repository.get_personnel_by_type(type_personnel, actif_only=actif_only)

    # Rechercher des membres du personnel
    def search_personnel(self, query, actif_only: bool = True):
        return self.repository.search_personnel(query, actif_only=actif_only)

    # Mettre à jour les données d'un membre du personnel
    def update_personnel(self, personnel, **data):
        id_user_data = data.pop("id_utilisateur", None) or data.pop("idUtilisateur", None)
        user_updates = {}

        if isinstance(id_user_data, dict):
            user_updates.update(id_user_data)
        elif isinstance(id_user_data, User):
            personnel.id_utilisateur = id_user_data

        for key in ["nom", "prenom", "email", "telephone", "date_naissance", "dateNaissance", "login", "motDePasse", "mot_de_passe", "motDePasseHash", "mot_de_passe_hash"]:
            if key in data:
                user_updates[key] = data.pop(key)

        data.pop("login", None)
        data.pop("motDePasse", None)
        data.pop("mot_de_passe", None)

        service_input = data.pop("id_service", None) or data.pop("idService", None) or data.get("serviceHopital") or data.get("service_hopital")
        if service_input:
            if isinstance(service_input, int):
                service_obj = self.service_service.get_service(service_input)
            elif isinstance(service_input, str):
                service_obj = self.service_service.get_or_create_service_by_nom(service_input)
            else:
                service_obj = service_input
            if service_obj:
                data["id_service"] = service_obj
                data["service_hopital"] = service_obj.get_nom_service_display()

        with transaction.atomic():
            if user_updates and personnel.id_utilisateur:
                self.user_service.updateUser(personnel.id_utilisateur, **user_updates)
            return self.repository.update_Personnel(personnel, **data)

    # Désactiver ou supprimer un membre du personnel
    def delete_personnel(self, personnel, hard=False):
        return self.repository.delete_personnel(personnel, hard=hard)
