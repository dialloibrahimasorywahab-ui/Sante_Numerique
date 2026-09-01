from .models import User


class UserRepository:

    # creation d'un utilisateur
    def createUser(self, **data):
        return User.objects.create(**data)

    # rechercher un utilisateur par son id
    def getUser(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # rechercher un utilisateur par son login ou email
    def getUserByLogin(self, login):
        from django.db.models import Q
        try:
            return User.objects.get(Q(login=login) | Q(email=login))
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return User.objects.filter(Q(login=login) | Q(email=login)).first()


    # recuperer tous les utilisateurs et les afficher
    def get_All_User(self):
        return User.objects.all()

    # filtrer les utilisateurs par rôle
    def getUsersByRole(self, role):
        return User.objects.filter(role__iexact=role)

    # rechercher les utilisateurs par nom, prénom, email ou login
    def searchUsers(self, query):
        from django.db.models import Q
        clean_q = str(query).strip()
        return User.objects.filter(
            Q(nom__icontains=clean_q) |
            Q(prenom__icontains=clean_q) |
            Q(email__icontains=clean_q) |
            Q(login__icontains=clean_q) |
            Q(telephone__icontains=clean_q)
        )


    # Mettre a jour les informations d'un utilisateur
    def update_User(self, user, **data):
        for field, value in data.items():
            setattr(user, field, value)

        user.save()
        return user

    # désactiver (soft delete) ou supprimer un utilisateur
    def delete_user(self, user, hard=False):
        if hard:
            user.delete()
            return True
        user.actif = False
        user.save(update_fields=["actif"])
        return True

        