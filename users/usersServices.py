from django.contrib.auth.hashers import make_password
from .usersRepositories import UserRepository


class UserService:

    # instanciation du repository pour avoir accès aux données du repository
    def __init__(self):
        self.repository = UserRepository()

    # creation d'un utilisateur dans service
    def createUser(self, **data):
        raw_password = data.pop("motDePasse", None) or data.get("motDePasseHash")
        if raw_password:
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
        from django.contrib.auth.hashers import check_password
        from django.utils import timezone
        user = self.repository.getUserByLogin(login)
        if user and user.actif and check_password(password, user.motDePasseHash):
            user.derniereConnexion = timezone.now()
            user.save(update_fields=["derniereConnexion"])
            return user
        return None

    # mettre a jour les informations d'un utilisateur
    def updateUser(self, user, **data):
        raw_password = data.pop("motDePasse", None)
        if raw_password:
            data["motDePasseHash"] = raw_password

        if "motDePasseHash" in data and data["motDePasseHash"]:
            if not data["motDePasseHash"].startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                data["motDePasseHash"] = make_password(data["motDePasseHash"])

        return self.repository.update_User(user, **data)

    # désactiver (archiver) ou supprimer un utilisateur
    def deleteUser(self, user, hard=False):
        return self.repository.delete_user(user, hard=hard)