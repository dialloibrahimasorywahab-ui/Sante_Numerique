from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Classe d'authentification JWT personnalisée qui extrait le token d'accès
    en priorité depuis le cookie HttpOnly 'access_token'.
    Si le cookie est absent, elle se replie sur le header standard 'Authorization: Bearer <token>'
    (utile pour Swagger UI, Postman et les tests).
    """

    def authenticate(self, request):
        # 1. Vérifier si le token est présent dans les cookies HttpOnly
        raw_token = request.COOKIES.get("access_token")

        if raw_token is not None:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, AuthenticationFailed):
                return None

        # 2. Repli sur le header Authorization: Bearer <token>
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
