from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT personnalisé qui enrichit le payload du token avec
    le rôle et le login de l'utilisateur.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des claims personnalisés dans le token JWT
        token['role'] = getattr(user, 'role', 'PATIENT')
        token['login'] = getattr(user, 'login', user.username)
        token['nom'] = getattr(user, 'nom', '')
        token['prenom'] = getattr(user, 'prenom', '')

        return token
