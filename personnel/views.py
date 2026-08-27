from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer
from .personnelSerializers import PersonnelSerializer
from .personnelServices import PersonnelService


personnel_service = PersonnelService()


# Enregistrement et listing du personnel
@extend_schema(
    tags=["Personnel"],
    summary="Lister ou créer un membre du personnel",
    description="Retourne la liste du personnel (GET avec filtres ?type=, ?search=) ou enregistre un nouveau membre du personnel (POST).",
    parameters=[
        OpenApiParameter(name="type", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par type de personnel (ex : INFIRMIER, ADMINISTRATIF)."),
        OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Recherche textuelle libre."),
    ],
    request=PersonnelSerializer,
    responses={200: PersonnelSerializer(many=True), 201: PersonnelSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
def create_personnel(request):
    if request.method == "GET":
        type_personnel = request.query_params.get("type") or request.query_params.get("category")
        search_q = request.query_params.get("search") or request.query_params.get("q")
        if type_personnel:
            personnels = personnel_service.get_personnel_by_type(type_personnel)
        elif search_q:
            personnels = personnel_service.search_personnel(search_q)
        else:
            personnels = personnel_service.get_all_personnel()
        serializer = PersonnelSerializer(personnels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
@extend_schema(
    tags=["Personnel"],
    summary="Lister le personnel",
    description="Retourne la liste du personnel, avec filtre optionnel par type/catégorie.",
    parameters=[
        OpenApiParameter(name="type", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par type de personnel (ex : INFIRMIER, ADMINISTRATIF). Alias : category."),
    ],
    responses={200: PersonnelSerializer(many=True)},
)
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
@extend_schema(
    tags=["Personnel"],
    summary="Lister le personnel par type",
    description="Retourne le personnel appartenant au type donné (ex : INFIRMIER, ADMINISTRATIF).",
    responses={200: PersonnelSerializer(many=True)},
)
@api_view(["GET"])
def get_personnel_by_type(request, type_personnel):
    personnels = personnel_service.get_personnel_by_type(type_personnel)
    serializer = PersonnelSerializer(personnels, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer, modifier ou supprimer un membre du personnel grâce à son ID
@extend_schema(
    tags=["Personnel"],
    summary="Récupérer, modifier ou supprimer un membre du personnel",
    description="Retourne, modifie ou supprime un membre du personnel à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=PersonnelSerializer,
    responses={200: PersonnelSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def get_personnel(request, personnel_id):
    if request.method in ["PUT", "PATCH"]:
        return update_personnel(request, personnel_id)
    elif request.method == "DELETE":
        return delete_personnel(request, personnel_id)

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
@extend_schema(
    tags=["Personnel"],
    summary="Modifier un membre du personnel",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un membre du personnel.",
    request=PersonnelSerializer,
    responses={200: PersonnelSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
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


# Désactiver (soft delete) ou supprimer un membre du personnel
@extend_schema(
    tags=["Personnel"],
    summary="Supprimer / désactiver un membre du personnel",
    description="Désactive (soft delete) la fiche du personnel, ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
def delete_personnel(request, personnel_id):
    personnel = personnel_service.get_Personnel(personnel_id)

    if personnel is None:
        return Response(
            {"message": "Membre du personnel introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    personnel_service.delete_personnel(personnel, hard=hard)

    if hard:
        return Response(
            {"message": "Fiche du personnel supprimée définitivement avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Compte personnel désactivé (archivé) avec succès."},
        status=status.HTTP_200_OK
    )
