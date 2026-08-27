import random
# pyrefly: ignore [missing-import]
from django.db import transaction
# pyrefly: ignore [missing-import]
from django.utils import timezone
from users.models import User
from users.usersServices import UserService
from .medecinRepositories import MedecinRepository


class MedecinService:

    # Instanciation des services et repositories
    def __init__(self):
        self.repository = MedecinRepository()
        self.user_service = UserService()

    # Enregistrement d'un médecin (prend en charge la création combinée User + Medecin)
    def createMedecin(self, **data):
        id_user_data = data.pop("idUtilisateur", None)

        def build_user_payload(u_info):
            prenom = u_info.get("prenom", "") or data.pop("prenom", "")
            nom = u_info.get("nom", "") or data.pop("nom", "")
            login = data.pop("login", None) or u_info.get("login")
            if not login:
                clean_p = prenom.lower().replace(" ", "") if prenom else "doc"
                clean_n = nom.lower().replace(" ", "") if nom else "medecin"
                login = f"dr_{clean_p}_{clean_n}_{random.randint(100, 999)}"
            email = u_info.get("email") or data.get("emailPro") or f"{login}@santenumerique.com"
            telephone = u_info.get("telephone") or data.get("telephonePro") or f"+22462{random.randint(1000000, 9999999)}"
            password = data.pop("motDePasse", "MedecinPass123!")

            return {
                "nom": nom or "Médecin",
                "prenom": prenom or "Docteur",
                "email": email,
                "telephone": telephone,
                "login": login,
                "motDePasseHash": password,
                "role": User.Role.MEDECIN,
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

        if user:
            data["idUtilisateur"] = user
            if not data.get("emailPro"):
                data["emailPro"] = user.email
            if not data.get("telephonePro"):
                data["telephonePro"] = user.telephone

        if "dateEmbauche" not in data or not data["dateEmbauche"]:
            data["dateEmbauche"] = timezone.now().date()

        if "numeroOrdre" not in data or not data["numeroOrdre"]:
            data["numeroOrdre"] = f"CNOM-{random.randint(10000, 99999)}"

        return self.repository.createMedecin(**data)

    # Rechercher et afficher un médecin par son ID
    def get_Medecin(self, medecin_id):
        return self.repository.get_medecin(medecin_id)

    # Récupérer tous les médecins
    def get_all_medecin(self):
        return self.repository.get_all_medecin()

    # Récupérer les médecins par spécialité / service
    def get_medecins_by_specialite(self, specialite):
        return self.repository.get_medecins_by_specialite(specialite)

    # Rechercher des médecins
    def search_medecins(self, query):
        return self.repository.search_medecins(query)

    # Mettre à jour les données d'un médecin
    def update_medecin(self, medecin, **data):
        id_user_data = data.pop("idUtilisateur", None)
        user_updates = {}

        if isinstance(id_user_data, dict):
            user_updates.update(id_user_data)
        elif isinstance(id_user_data, User):
            medecin.idUtilisateur = id_user_data

        for key in ["nom", "prenom", "email", "telephone", "dateNaissance", "login", "motDePasse", "motDePasseHash"]:
            if key in data:
                user_updates[key] = data.pop(key)

        data.pop("login", None)
        data.pop("motDePasse", None)

        with transaction.atomic():
            if user_updates and medecin.idUtilisateur:
                self.user_service.updateUser(medecin.idUtilisateur, **user_updates)
            return self.repository.update_Medecin(medecin, **data)

    # Désactiver ou supprimer un médecin
    def delete_medecin(self, medecin, hard=False):
        return self.repository.delete_medecin(medecin, hard=hard)

