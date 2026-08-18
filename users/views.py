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
        user = user_service.createUser(**serializer.validated_data)
        serializer = UserSerializers(user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
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


# recuperer et afficher tous les utilisateurs
@api_view(["GET"])
def get_all_user(request):
    users = user_service.getAllUser()

    serializer = UserSerializers(users, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Connexion / Authentification d'un utilisateur (sans JWT)
@api_view(["POST"])
def login_user(request):
    login = request.data.get("login")
    password = request.data.get("motDePasse") or request.data.get("password")

    if not login or not password:
        return Response(
            {"message": "Le login et le mot de passe sont requis"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = user_service.loginUser(login, password)

    if user is None:
        return Response(
            {"message": "Identifiants invalides ou compte inactif"},
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
        user = user_service.updateUser(user, **serializer.validated_data)
        serializer = UserSerializers(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# supprimer ou archiver un utilisateur
@api_view(["DELETE"])
def delete_user(request, user_id):
    user = user_service.getUser(user_id)

    if user is None:
        return Response(
            {"message": "Utilisateur introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    user_service.deleteUser(user)

    return Response(
        {"message": "Utilisateur supprimé avec succès"},
        status=status.HTTP_204_NO_CONTENT
    )