from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User
from .usersRepositories import UserRepository


class UserService:

    # instanciation du repository pour avoir accès aux données du repository
    def __init__(self):
        self.repository = UserRepository()

    # creation d'un utilisateur dans service
    def createUser(self, **data):
        raw_password = data.pop("motDePasse", None) or data.get("motDePasseHash")
        if raw_password:
            if not raw_password.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                temp_user = User(
                    login=data.get("login", ""),
                    email=data.get("email", ""),
                    nom=data.get("nom", ""),
                    prenom=data.get("prenom", ""),
                )
                validate_password(raw_password, user=temp_user)
            data["motDePasseHash"] = make_password(raw_password)
        return self.repository.createUser(**data)

    # recuperation d'un utilisateur dans service grace a son id
    def getUser(self, userId):
        return self.repository.getUser(userId)

    # recuperer tous les utilisateur dans service
    def getAllUser(self):
        return self.repository.get_All_User()

    def getUsersByRole(self, role):
        return self.repository.getUsersByRole(role)

    def searchUsers(self, query):
        return self.repository.searchUsers(query)

    # authentification d'un utilisateur par son login et mot de passe (sans JWT)
    def loginUser(self, login, password):
        user = self.repository.getUserByLogin(login)
        if user and user.actif and check_password(password, user.motDePasseHash):
            user.derniereConnexion = timezone.now()
            user.save(update_fields=["last_login"])
            return user
        return None

    # mettre a jour les informations d'un utilisateur
    def updateUser(self, user, **data):
        raw_password = data.pop("motDePasse", None)
        if raw_password:
            if not raw_password.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                validate_password(raw_password, user=user)
            data["motDePasseHash"] = raw_password

        if "motDePasseHash" in data and data["motDePasseHash"]:
            if not data["motDePasseHash"].startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                validate_password(data["motDePasseHash"], user=user)
                data["motDePasseHash"] = make_password(data["motDePasseHash"])

        return self.repository.update_User(user, **data)

    # changer le mot de passe de maniere securisee
    def changePassword(self, user, old_password, new_password, confirm_password=None):
        if not user.check_password(old_password):
            raise ValueError("L'ancien mot de passe est incorrect.")

        if confirm_password is not None and new_password != confirm_password:
            raise ValueError("Les deux mots de passe ne correspondent pas.")

        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return user

    # désactiver (archiver) ou supprimer un utilisateur
    def deleteUser(self, user, hard=False):
        return self.repository.delete_user(user, hard=hard)