from django.contrib.auth.hashers import make_password
from .usersRepositories import UserRepository


class UserService:

    # instanciation du repository pour avoir accès aux données du repository
    def __init__(self):
        self.repository = UserRepository()

    # creation d'un utilisateur dans service
    def createUser(self, **data):
        if "motDePasseHash" in data and data["motDePasseHash"]:
            data["motDePasseHash"] = make_password(data["motDePasseHash"])
        return self.repository.createUser(**data)

    # recuperation d'un utilisateur dans service grace a son id
    def getUser(self, userId):
        return self.repository.getUser(userId)

    # recuperer tous les utilisateur dans service
    def getAllUser(self):
        return self.repository.get_All_User()

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
        if "motDePasseHash" in data and data["motDePasseHash"]:
            if not data["motDePasseHash"].startswith(("pbkdf2_", "bcrypt", "argon2")):
                data["motDePasseHash"] = make_password(data["motDePasseHash"])
        return self.repository.update_User(user, **data)

    # archiver un utilisateur
    def deleteUser(self, user):
        return self.repository.delete_user(user)