import random
import secrets
from django.db import transaction
from django.utils import timezone
from common.services import BaseService
from users.models import User
from users.usersServices import UserService
from .models import Medecin
from .medecinRepositories import MedecinRepository


class MedecinService(BaseService[Medecin]):
    """
    Service métier pour la gestion des médecins et la synchronisation avec le compte utilisateur.
    """
    def __init__(self):
        self.repository = MedecinRepository()
        self.user_service = UserService()
        super().__init__(repository=self.repository)

    # Enregistrement d'un médecin (prend en charge la création combinée User + Medecin)
    def createMedecin(self, **data):
        id_user_data = data.pop("idUtilisateur", None) or data.pop("id_utilisateur", None)

        def build_user_payload(u_info):
            prenom = u_info.get("prenom", "") or data.pop("prenom", "")
            nom = u_info.get("nom", "") or data.pop("nom", "")
            login = data.pop("login", None) or u_info.get("login")
            if not login:
                clean_p = prenom.lower().replace(" ", "") if prenom else "doc"
                clean_n = nom.lower().replace(" ", "") if nom else "medecin"
                login = f"dr_{clean_p}_{clean_n}_{random.randint(100, 999)}"
            email = u_info.get("email") or data.get("emailPro") or data.get("email_pro") or f"{login}@santenumerique.com"
            telephone = u_info.get("telephone") or data.get("telephonePro") or data.get("telephone_pro") or f"+22462{random.randint(1000000, 9999999)}"
            password = data.pop("motDePasse", data.pop("mot_de_passe", None)) or secrets.token_urlsafe(16)

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
        data.pop("mot_de_passe", None)

        if user:
            data["id_utilisateur"] = user
            if not data.get("emailPro") and not data.get("email_pro"):
                data["email_pro"] = user.email
            if not data.get("telephonePro") and not data.get("telephone_pro"):
                data["telephone_pro"] = user.telephone

        if "dateEmbauche" not in data and "date_embauche" not in data:
            data["date_embauche"] = timezone.now().date()

        if "numeroOrdre" not in data and "numero_ordre" not in data:
            data["numero_ordre"] = f"CNOM-{random.randint(10000, 99999)}"

        return self.repository.createMedecin(**data)

    # Rechercher et afficher un médecin par son ID
    def get_medecin(self, medecin_id):
        return self.repository.get_medecin(medecin_id)

    def get_Medecin(self, medecin_id):
        return self.get_medecin(medecin_id)

    # Récupérer tous les médecins
    def get_all_medecin(self, actif_only: bool = True):
        return self.repository.get_all_medecin(actif_only=actif_only)

    # Récupérer les médecins par spécialité / service
    def get_medecins_by_specialite(self, specialite, actif_only: bool = True):
        return self.repository.get_medecins_by_specialite(specialite, actif_only=actif_only)

    # Rechercher des médecins
    def search_medecins(self, query, actif_only: bool = True):
        return self.repository.search_medecins(query, actif_only=actif_only)

    # Mettre à jour les données d'un médecin
    def update_medecin(self, medecin, **data):
        id_user_data = data.pop("idUtilisateur", None) or data.pop("id_utilisateur", None)
        user_updates = {}

        if isinstance(id_user_data, dict):
            user_updates.update(id_user_data)
        elif isinstance(id_user_data, User):
            medecin.id_utilisateur = id_user_data

        for key in ["nom", "prenom", "email", "telephone", "dateNaissance", "date_naissance", "login", "motDePasse", "mot_de_passe", "motDePasseHash", "mot_de_passe_hash"]:
            if key in data:
                user_updates[key] = data.pop(key)

        data.pop("login", None)
        data.pop("motDePasse", None)
        data.pop("mot_de_passe", None)

        with transaction.atomic():
            if user_updates and medecin.id_utilisateur:
                self.user_service.updateUser(medecin.id_utilisateur, **user_updates)
            return self.repository.update_Medecin(medecin, **data)

    # Désactiver ou supprimer un médecin
    def delete_medecin(self, medecin, hard=False):
        return self.repository.delete_medecin(medecin, hard=hard)
