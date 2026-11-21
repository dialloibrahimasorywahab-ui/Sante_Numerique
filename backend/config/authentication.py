from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthentication(JWTAuthentication):
    """
    Classe d'authentification JWT personnalisée qui extrait le token d'accès
    en priorité depuis le cookie HttpOnly 'access_token'.
    Si le cookie est absent, elle se replie sur le header standard 'Authorization: Bearer <token>'
    ou sur le paramètre de requête 'token' (idéal pour EventSource / SSE).
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

        # 2. Repli sur le paramètre query 'token' (utile pour EventSource SSE)
        query_token = None
        if hasattr(request, "query_params"):
            query_token = request.query_params.get("token")
        if not query_token and hasattr(request, "GET"):
            query_token = request.GET.get("token")

        if query_token:
            try:
                validated_token = self.get_validated_token(query_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, AuthenticationFailed):
                return None

        # 3. Repli sur le header standard Authorization: Bearer <token>
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


class CookieJWTScheme(OpenApiAuthenticationExtension):
    target_class = 'config.authentication.CookieJWTAuthentication'
    name = 'cookieAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token',
            'description': "Authentification par cookie HttpOnly 'access_token', header 'Authorization: Bearer <token>' ou query 'token'."
        }
