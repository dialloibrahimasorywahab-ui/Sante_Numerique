from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .medecinSerializers import MedecinSerializer
from .medecinServices import MedecinService


medecin_service = MedecinService()


# Enregistrement et listing des médecins
@extend_schema(
    tags=["Médecins"],
    summary="Lister ou créer un médecin",
    description="Retourne la liste des médecins (GET avec filtres ?service=, ?specialite=, ?search=, ?all=) ou enregistre un nouveau médecin (POST).",
    parameters=[
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                          description="Inclure aussi les médecins inactifs si true."),
        OpenApiParameter(name="service", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par service ou spécialité (alias : specialite)."),
        OpenApiParameter(name="specialite", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par spécialité."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=MedecinSerializer,
    responses={200: MedecinSerializer(many=True), 201: MedecinSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def create_medecin(request):
    if request.method == "GET":
        actif_only = request.query_params.get("all", "false").lower() != "true"
        specialite = request.query_params.get("service") or request.query_params.get("specialite")
        search_q = request.query_params.get("search") or request.query_params.get("q")
        if specialite:
            medecins = medecin_service.get_medecins_by_specialite(specialite, actif_only=actif_only)
        elif search_q:
            medecins = medecin_service.search_medecins(search_q, actif_only=actif_only)
        else:
            medecins = medecin_service.get_all_medecin(actif_only=actif_only)
        return paginate_response(medecins, request, MedecinSerializer)

    if not request.user.is_authenticated or getattr(request.user, "role", None) != "ADMINISTRATEUR":
        return Response({"message": "Seul un administrateur peut enregistrer un médecin."}, status=status.HTTP_403_FORBIDDEN)

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
                {"error": "Impossible d'enregistrer ce médecin.", "detail": str(e)},
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
    description="Retourne la liste de tous les médecins avec filtres optionnels ?all=, ?service=, ?specialite=.",
    parameters=[
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                          description="Inclure aussi les médecins inactifs si true."),
        OpenApiParameter(name="service", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par service ou spécialité (alias : specialite)."),
        OpenApiParameter(name="specialite", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par spécialité."),
        *PAGINATION_PARAMS,
    ],
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_medecin(request):
    actif_only = request.query_params.get("all", "false").lower() != "true"
    specialite = request.query_params.get("service") or request.query_params.get("specialite")
    if specialite:
        medecins = medecin_service.get_medecins_by_specialite(specialite, actif_only=actif_only)
    else:
        medecins = medecin_service.get_all_medecin(actif_only=actif_only)

    return paginate_response(medecins, request, MedecinSerializer)


# Récupérer les médecins d'un service / spécialité
@extend_schema(
    tags=["Médecins"],
    summary="Lister les médecins d'une spécialité",
    description="Retourne les médecins rattachés à la spécialité/service donné(e).",
    parameters=[*PAGINATION_PARAMS],
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_medecins_by_specialite(request, specialite):
    medecins = medecin_service.get_medecins_by_specialite(specialite)
    return paginate_response(medecins, request, MedecinSerializer)


# Récupérer, modifier ou supprimer un médecin grâce à son ID
@extend_schema(
    tags=["Médecins"],
    summary="Récupérer, modifier ou supprimer un médecin",
    description="Retourne, modifie ou supprime un médecin par son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=MedecinSerializer,
    responses={200: MedecinSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def get_medecin(request, medecin_id):
    if request.method in ["PUT", "PATCH"]:
        deny = deny_unless_owner_or_staff(request, medecin_id, id_field="id_medecin")
        if deny:
            return deny
        return update_medecin(request, medecin_id)
    elif request.method == "DELETE":
        if not request.user.is_authenticated or getattr(request.user, "role", None) != "ADMINISTRATEUR":
            return Response({"message": "Accès non autorisé."}, status=status.HTTP_403_FORBIDDEN)
        return delete_medecin(request, medecin_id)

    medecin = medecin_service.get_medecin(medecin_id)

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
@permission_classes([IsAuthenticated])
def update_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, medecin)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MedecinSerializer(medecin, data=request.data, partial=partial, context={"request": request})

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
@permission_classes([IsAdmin])
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
