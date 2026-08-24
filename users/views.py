from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .usersSerializers import UserSerializers
from .usersServices import UserService


user_service = UserService()


# enregistrement d'un utilisateur
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