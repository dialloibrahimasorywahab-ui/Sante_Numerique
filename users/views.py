from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .usersSerializers import UserSerializers
from .usersServices import UserService


user_service = UserService()


# enregistrement d'un utilisateur
@extend_schema(
    tags=["Utilisateurs"],
    summary="Créer un utilisateur",
    description="Enregistre un nouvel utilisateur (compte de connexion à l'application).",
    request=UserSerializers,
    responses={201: UserSerializers, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
def create_user(request):
    serializer = UserSerializers(data=request.data)

    if serializer.is_valid():
        try:
            user = user_service.createUser(**serializer.validated_data)
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


# recuperer et afficher un utilisateur grace a son id
@extend_schema(
    tags=["Utilisateurs"],
    summary="Récupérer un utilisateur",
    description="Retourne un utilisateur à partir de son identifiant.",
    responses={200: UserSerializers, 404: MessageResponseSerializer},
)
@api_view(["GET"])
def get_user(request, user_id):
    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

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
        OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Recherche libre (alias : q)."),
    ],
    responses={200: UserSerializers(many=True)},
)
@api_view(["GET"])
def get_all_user(request):
    role = request.query_params.get("role")
    search_q = request.query_params.get("search") or request.query_params.get("q")

    if role:
        users = user_service.getUsersByRole(role)
    elif search_q:
        users = user_service.searchUsers(search_q)
    else:
        users = user_service.getAllUser()

    serializer = UserSerializers(users, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Connexion / Authentification d'un utilisateur (par login ou email)
@extend_schema(
    tags=["Utilisateurs"],
    summary="Se connecter",
    description="Authentifie un utilisateur par login (ou email) et mot de passe.",
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
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )



# Mettre à jour les informations d'un utilisateur
@extend_schema(
    tags=["Utilisateurs"],
    summary="Modifier un utilisateur",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un utilisateur.",
    request=UserSerializers,
    responses={200: UserSerializers, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
def update_user(request, user_id):
    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = UserSerializers(user, data=request.data, partial=partial)

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
