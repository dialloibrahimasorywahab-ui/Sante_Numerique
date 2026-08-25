from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer
from .medecinSerializers import MedecinSerializer
from .medecinServices import MedecinService


medecin_service = MedecinService()


# Enregistrement d'un médecin
@extend_schema(
    tags=["Médecins"],
    summary="Créer un médecin",
    description="Enregistre un nouveau médecin (et le compte utilisateur associé).",
    request=MedecinSerializer,
    responses={201: MedecinSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
def create_medecin(request):
    serializer = MedecinSerializer(data=request.data)

    if serializer.is_valid():
        try:
            medecin = medecin_service.createMedecin(**serializer.validated_data)
            serializer = MedecinSerializer(medecin)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un médecin ou utilisateur avec cet identifiant, email, téléphone ou numéro d'ordre existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer tous les médecins (avec support du filtre ?service=... ou ?specialite=...)
@extend_schema(
    tags=["Médecins"],
    summary="Lister les médecins",
    description="Retourne la liste des médecins, avec filtre optionnel par service/spécialité.",
    parameters=[
        OpenApiParameter(name="service", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par service ou spécialité (alias : specialite)."),
        OpenApiParameter(name="specialite", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par spécialité."),
    ],
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
def get_all_medecin(request):
    specialite = request.query_params.get("service") or request.query_params.get("specialite")
    if specialite:
        medecins = medecin_service.get_medecins_by_specialite(specialite)
    else:
        medecins = medecin_service.get_all_medecin()

    serializer = MedecinSerializer(medecins, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer les médecins d'un service / spécialité
@extend_schema(
    tags=["Médecins"],
    summary="Lister les médecins d'une spécialité",
    description="Retourne les médecins rattachés à la spécialité/service donné(e).",
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
def get_medecins_by_specialite(request, specialite):
    medecins = medecin_service.get_medecins_by_specialite(specialite)
    serializer = MedecinSerializer(medecins, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer et afficher un médecin grâce à son ID
@extend_schema(
    tags=["Médecins"],
    summary="Récupérer un médecin",
    description="Retourne un médecin à partir de son identifiant.",
    responses={200: MedecinSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET"])
def get_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = MedecinSerializer(medecin)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Modifier les informations d'un médecin
@extend_schema(
    tags=["Médecins"],
    summary="Modifier un médecin",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un médecin.",
    request=MedecinSerializer,
    responses={200: MedecinSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
def update_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MedecinSerializer(medecin, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            medecin = medecin_service.update_medecin(medecin, **serializer.validated_data)
            serializer = MedecinSerializer(medecin)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un médecin ou utilisateur avec cet identifiant, email, téléphone ou numéro d'ordre existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Désactiver (soft delete) ou supprimer un médecin
@extend_schema(
    tags=["Médecins"],
    summary="Supprimer / désactiver un médecin",
    description="Désactive (soft delete) la fiche médecin, ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
def delete_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    medecin_service.delete_medecin(medecin, hard=hard)

    if hard:
        return Response(
            {"message": "Fiche médecin supprimée définitivement avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Compte médecin désactivé (archivé) avec succès."},
        status=status.HTTP_200_OK
    )
