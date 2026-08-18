from django.db import transaction
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
        # Extraction des champs utilisateur imbriqués sous idUtilisateur s'ils existent (depuis serializer source)
        id_user_data = data.pop("idUtilisateur", None)

        if isinstance(id_user_data, User):
            user = id_user_data
        elif isinstance(id_user_data, dict):
            user_info = id_user_data
            login = data.pop("login", user_info.get("login", ""))
            password = data.pop("motDePasse", "DefaultPass123!")

            user_payload = {
                "nom": user_info.get("nom", ""),
                "prenom": user_info.get("prenom", ""),
                "email": user_info.get("email", data.get("emailPro", "")),
                "telephone": user_info.get("telephone", data.get("telephonePro", "")),
                "login": login,
                "motDePasseHash": password,
                "role": User.Role.MEDECIN,
                "actif": True,
            }
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)
        elif id_user_data is None and ("nom" in data or "login" in data):
            user_payload = {
                "nom": data.pop("nom", ""),
                "prenom": data.pop("prenom", ""),
                "email": data.pop("email", data.get("emailPro", "")),
                "telephone": data.pop("telephone", data.get("telephonePro", "")),
                "login": data.pop("login", ""),
                "motDePasseHash": data.pop("motDePasse", "DefaultPass123!"),
                "role": User.Role.MEDECIN,
                "actif": True,
            }
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)
        else:
            user = None

        # Nettoyage des champs virtuels
        data.pop("login", None)
        data.pop("motDePasse", None)

        if user:
            data["idUtilisateur"] = user
            if not data.get("emailPro"):
                data["emailPro"] = user.email
            if not data.get("telephonePro"):
                data["telephonePro"] = user.telephone

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

    # Mettre à jour les données d'un médecin
    def update_medecin(self, medecin, **data):
        return self.repository.update_Medecin(medecin, **data)

    # Supprimer un médecin
    def delete_medecin(self, medecin):
        return self.repository.delete_medecin(medecin)
