from django.conf import settings
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from config.pagination import paginate_response
from config.permissions import IsAdmin, IsOwnerOrStaff, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .authentication import RoleTokenObtainPairSerializer
from .usersSerializers import UserSerializers
from .usersServices import UserService


user_service = UserService()


def set_jwt_cookies(response, refresh_token):
    """Dépose les cookies sécurisés HttpOnly access_token et refresh_token sur la réponse HTTP."""
    access_token = refresh_token.access_token
    response.set_cookie(
        key="access_token",
        value=str(access_token),
        max_age=3600,
        httponly=True,
        secure=getattr(settings, 'JWT_COOKIE_SECURE', False),
        samesite=getattr(settings, 'JWT_COOKIE_SAMESITE', 'Strict'),
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        max_age=2592000,
        httponly=True,
        secure=getattr(settings, 'JWT_COOKIE_SECURE', False),
        samesite=getattr(settings, 'JWT_COOKIE_SAMESITE', 'Strict'),
        path="/users/token/refresh/",
    )
    return response


def delete_jwt_cookies(response):
    """Supprime les cookies d'authentification JWT."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/users/token/refresh/")
    return response


# Enregistrement et listing des utilisateurs
@extend_schema(
    tags=["Utilisateurs"],
    summary="Lister ou créer un utilisateur",
    description="Retourne la liste des utilisateurs (GET avec filtres optionnels ?role=, ?search=) ou enregistre un nouvel utilisateur (POST).",
    parameters=[
        OpenApiParameter(name="role", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre les utilisateurs par rôle."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=UserSerializers,
    responses={200: UserSerializers(many=True), 201: UserSerializers, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def create_user(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response({"detail": "Informations d'authentification non fournies."}, status=status.HTTP_401_UNAUTHORIZED)
        if getattr(request.user, "role", None) not in ["ADMINISTRATEUR", "MEDECIN", "INFIRMIER"]:
            return Response({"error": "Accès refusé. Réservé au personnel et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        role = request.query_params.get("role")
        search_q = request.query_params.get("search") or request.query_params.get("q")

        if role:
            users = user_service.getUsersByRole(role)
        elif search_q:
            users = user_service.searchUsers(search_q)
        else:
            users = user_service.getAllUser()

        return paginate_response(users, request, UserSerializers)

    serializer = UserSerializers(data=request.data, context={"request": request})

    if serializer.is_valid():
        validated_data = serializer.validated_data.copy()
        requested_role = validated_data.get("role", "PATIENT")

        # Si l'utilisateur n'est pas un administrateur connecté, seuls les comptes PATIENT sont autorisés
        is_admin = request.user.is_authenticated and getattr(request.user, "role", None) == "ADMINISTRATEUR"
        if not is_admin:
            if requested_role and requested_role != "PATIENT":
                return Response(
                    {"error": "Seul un administrateur peut créer un compte avec le rôle Médecin, Infirmier ou Administrateur."},
                    status=status.HTTP_403_FORBIDDEN
                )
            validated_data["role"] = "PATIENT"

        try:
            user = user_service.createUser(**validated_data)
            serializer = UserSerializers(user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un utilisateur avec cet email, téléphone ou login existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer, modifier ou supprimer un utilisateur grâce à son ID
@extend_schema(
    tags=["Utilisateurs"],
    summary="Récupérer, modifier ou supprimer un utilisateur",
    description="Retourne, modifie ou supprime un utilisateur à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=UserSerializers,
    responses={200: UserSerializers, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    if request.method in ["PUT", "PATCH"]:
        return update_user(request, user_id)
    elif request.method == "DELETE":
        return delete_user(request, user_id)

    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, user)

    serializer = UserSerializers(user)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# recuperer et afficher tous les utilisateurs (avec filtres ?role=... ou ?search=...)
@extend_schema(
    tags=["Utilisateurs"],
    summary="Lister les utilisateurs",
    description="Retourne la liste des utilisateurs, avec filtre optionnel par rôle ou recherche libre.",
    parameters=[
        OpenApiParameter(name="role", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre les utilisateurs par rôle."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    responses={200: UserSerializers(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_all_user(request):
    role = request.query_params.get("role")
    search_q = request.query_params.get("search") or request.query_params.get("q")

    if role:
        users = user_service.getUsersByRole(role)
    elif search_q:
        users = user_service.searchUsers(search_q)
    else:
        users = user_service.getAllUser()

    return paginate_response(users, request, UserSerializers)


# Connexion / Authentification d'un utilisateur (par login ou email) avec tokens HttpOnly
@extend_schema(
    tags=["Utilisateurs"],
    summary="Se connecter (Authentification JWT)",
    description="Authentifie un utilisateur par login (ou email) et mot de passe, et dépose les tokens JWT en cookies HttpOnly sécurisés.",
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "login": serializers.CharField(required=False, help_text="Login de l'utilisateur"),
            "email": serializers.CharField(required=False, help_text="Email (alternative au login)"),
            "password": serializers.CharField(required=False, style={"input_type": "password"}),
            "motDePasse": serializers.CharField(required=False, style={"input_type": "password"}),
        },
    ),
    responses={
        200: UserSerializers,
        400: MessageResponseSerializer,
        401: MessageResponseSerializer,
        403: MessageResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    login = request.data.get("login") or request.data.get("email") or request.data.get("username")
    password = request.data.get("motDePasse") or request.data.get("password") or request.data.get("motDePasseHash")

    if not login or not password:
        return Response(
            {"message": "Le login (ou email) et le mot de passe sont requis"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = user_service.loginUser(login, password)

    if user is None:
        existing_user = user_service.repository.getUserByLogin(login)
        if existing_user and not existing_user.actif:
            return Response(
                {"message": "Compte désactivé. Veuillez contacter l'administrateur."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {"message": "Identifiants invalides"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = UserSerializers(user)
    response = Response(
        serializer.data,
        status=status.HTTP_200_OK
    )

    # Poser les tokens JWT en cookies HttpOnly
    refresh = RoleTokenObtainPairSerializer.get_token(user)
    set_jwt_cookies(response, refresh)

    return response


# Déconnexion d'un utilisateur (suppression cookies et blacklistage du refresh token)
@extend_schema(
    tags=["Utilisateurs"],
    summary="Se déconnecter",
    description="Invalide le refresh token et supprime les cookies HttpOnly.",
    responses={200: MessageResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_user(request):
    raw_refresh = request.COOKIES.get("refresh_token") or request.data.get("refresh")
    if raw_refresh:
        try:
            token = RefreshToken(raw_refresh)
            token.blacklist()
        except Exception:
            pass

    response = Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)
    delete_jwt_cookies(response)
    return response


# Déconnexion de toutes les sessions (blacklistage global)
@extend_schema(
    tags=["Utilisateurs"],
    summary="Déconnecter toutes les sessions",
    description="Invalide toutes les sessions et tokens de l'utilisateur connecté.",
    responses={200: MessageResponseSerializer, 401: MessageResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_all_users(request):
    tokens = OutstandingToken.objects.filter(user=request.user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)

    response = Response(
        {"message": "Déconnexion de toutes les sessions réussie."},
        status=status.HTTP_200_OK
    )
    delete_jwt_cookies(response)
    return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Vue de rafraîchissement des tokens qui extrait le refresh token depuis le cookie HttpOnly
    'refresh_token', effectue la rotation et réémet les nouveaux cookies HttpOnly.
    """

    @extend_schema(
        tags=["Utilisateurs"],
        summary="Rafraîchir le token d'accès (Cookie HttpOnly)",
        description="Lit le cookie HttpOnly 'refresh_token', effectue la rotation et dépose les nouveaux cookies sécurisés.",
        responses={200: MessageResponseSerializer, 401: MessageResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        raw_refresh = request.COOKIES.get("refresh_token") or request.data.get("refresh")
        if not raw_refresh:
            response = Response(
                {"message": "Refresh token manquant dans les cookies."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            delete_jwt_cookies(response)
            return response

        data = {"refresh": raw_refresh}
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            response = Response(
                {"message": "Refresh token invalide ou expiré.", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
            delete_jwt_cookies(response)
            return response
        except Exception as e:
            response = Response(
                {"message": "Erreur lors du rafraîchissement du token.", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
            delete_jwt_cookies(response)
            return response

        validated = serializer.validated_data
        access_token = validated.get("access")
        new_refresh = validated.get("refresh")

        response = Response(
            {"message": "Token rafraîchi avec succès."},
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            max_age=3600,
            httponly=True,
            secure=getattr(settings, 'JWT_COOKIE_SECURE', False),
            samesite=getattr(settings, 'JWT_COOKIE_SAMESITE', 'Strict'),
            path="/",
        )

        if new_refresh:
            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                max_age=2592000,
                httponly=True,
                secure=getattr(settings, 'JWT_COOKIE_SECURE', False),
                samesite=getattr(settings, 'JWT_COOKIE_SAMESITE', 'Strict'),
                path="/users/token/refresh/",
            )

        return response



# Mettre à jour les informations d'un utilisateur
@extend_schema(
    tags=["Utilisateurs"],
    summary="Modifier un utilisateur",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un utilisateur.",
    request=UserSerializers,
    responses={200: UserSerializers, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, user)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = UserSerializers(user, data=request.data, partial=partial, context={"request": request})

    if serializer.is_valid():
        try:
            user = user_service.updateUser(user, **serializer.validated_data)
            serializer = UserSerializers(user)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un utilisateur avec cet email, téléphone ou login existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# désactiver (soft delete) ou supprimer définitivement un utilisateur
@extend_schema(
    tags=["Utilisateurs"],
    summary="Supprimer / désactiver un utilisateur",
    description="Désactive (soft delete) le compte utilisateur, ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_user(request, user_id):
    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    user_service.deleteUser(user, hard=hard)

    if hard:
        return Response(
            {"message": "Utilisateur supprimé définitivement de la base de données avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Compte utilisateur désactivé (archivé) avec succès.", "actif": False},
        status=status.HTTP_200_OK
    )
