from .models import User


class UserRepository:

    # creation d'un utilisateur
    def createUser(self, **data):
        return User.objects.create(**data)

    # rechercher un utilisateur par son id
    def getUser(self, user_id):
        try:
            return User.objects.get(idUser=user_id)
        except User.DoesNotExist:
            return None

    # rechercher un utilisateur par son login
    def getUserByLogin(self, login):
        try:
            return User.objects.get(login=login)
        except User.DoesNotExist:
            return None

    # recuperer tous les utilisateurs et les afficher
    def get_All_User(self):
        return User.objects.all()

    # Mettre a jour les informations d'un utilisateur
    def update_User(self, user, **data):
        for field, value in data.items():
            setattr(user, field, value)

        user.save()
        return user

    # supprimer ou archiver un utilisateur
    def delete_user(self, user):
        user.delete()
        