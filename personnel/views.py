from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .personnelSerializers import PersonnelSerializer
from .personnelServices import PersonnelService


personnel_service = PersonnelService()


# Enregistrement d'un membre du personnel
@api_view(["POST"])
def create_personnel(request):
    serializer = PersonnelSerializer(data=request.data)

    if serializer.is_valid():
        try:
            personnel = personnel_service.createPersonnel(**serializer.validated_data)
            serializer = PersonnelSerializer(personnel)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un membre du personnel ou utilisateur avec cet identifiant, matricule, email ou téléphone existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer tout le personnel (avec filtre ?type=...)
@api_view(["GET"])
def get_all_personnel(request):
    type_personnel = request.query_params.get("type") or request.query_params.get("category")
    if type_personnel:
        personnels = personnel_service.get_personnel_by_type(type_personnel)
    else:
        personnels = personnel_service.get_all_personnel()

    serializer = PersonnelSerializer(personnels, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer le personnel par type (ex: INFIRMIER, ADMINISTRATIF)
@api_view(["GET"])
def get_personnel_by_type(request, type_personnel):
    personnels = personnel_service.get_personnel_by_type(type_personnel)
    serializer = PersonnelSerializer(personnels, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer et afficher un membre du personnel grâce à son ID
@api_view(["GET"])
def get_personnel(request, personnel_id):
    personnel = personnel_service.get_Personnel(personnel_id)

    if personnel is None:
        return Response(
            {"message": "Membre du personnel introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PersonnelSerializer(personnel)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Modifier les informations d'un membre du personnel
@api_view(["PUT", "PATCH"])
def update_personnel(request, personnel_id):
    personnel = personnel_service.get_Personnel(personnel_id)

    if personnel is None:
        return Response(
            {"message": "Membre du personnel introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = PersonnelSerializer(personnel, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            personnel = personnel_service.update_personnel(personnel, **serializer.validated_data)
            serializer = PersonnelSerializer(personnel)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un membre du personnel ou utilisateur avec cet identifiant, matricule, email ou téléphone existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Supprimer un membre du personnel
@api_view(["DELETE"])
def delete_personnel(request, personnel_id):
    personnel = personnel_service.get_Personnel(personnel_id)

    if personnel is None:
        return Response(
            {"message": "Membre du personnel introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    personnel_service.delete_personnel(personnel)

    return Response(
        {"message": "Membre du personnel supprimé avec succès"},
        status=status.HTTP_204_NO_CONTENT
    )
