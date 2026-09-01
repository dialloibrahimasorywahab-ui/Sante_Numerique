from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    PAGINATION_PARAMS,
    SEARCH_PARAM,
)
from .fraisSerializers import FraisConsultationSerializer
from .fraisServices import FraisConsultationService

frais_service = FraisConsultationService()


@extend_schema(
    tags=["Frais de Consultation"],
    summary="Lister ou créer des frais de consultation",
    description="GET: Liste l'ensemble des frais de consultation avec filtres (statut, all).\nPOST: Enregistre un nouveau frais.",
    parameters=[
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Filtrer par statut (EN_ATTENTE, PAYE, ANNULE)."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les frais inactifs si true."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=FraisConsultationSerializer,
    responses={
        200: FraisConsultationSerializer(many=True),
        201: FraisConsultationSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsStaffOrAdmin])
def frais_list_create_view(request):
    if request.method == "GET":
        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = frais_service.repository.get_all_frais(actif_only=actif_only)

        statut_param = request.query_params.get("statut")
        if statut_param:
            qs = qs.filter(statut=statut_param)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(description__icontains=search)

        return paginate_response(qs, request, FraisConsultationSerializer)

    elif request.method == "POST":
        serializer = FraisConsultationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                frais = frais_service.creer_frais(**serializer.validated_data)
                return Response(FraisConsultationSerializer(frais).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Frais de Consultation"],
    summary="Détail ou mise à jour de frais de consultation",
    description="Accède aux détails d'un frais ou met à jour ses informations.",
    request=FraisConsultationSerializer,
    responses={
        200: FraisConsultationSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def frais_detail_view(request, pk):
    frais = frais_service.repository.get_frais_by_id(pk)
    if not frais:
        return Response({"error": f"Frais #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, frais)

    if request.method == "GET":
        return Response(FraisConsultationSerializer(frais).data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
        return Response({"error": "Action réservée au personnel médical et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

    partial = (request.method == "PATCH")
    serializer = FraisConsultationSerializer(frais, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = frais_service.mettre_a_jour_frais(pk, **serializer.validated_data)
            return Response(FraisConsultationSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Frais de Consultation"],
    summary="Enregistrer le règlement d'un frais",
    description="Passe le statut du frais à PAYE et enregistre la date et l'heure du règlement.",
    request=FraisConsultationSerializer,
    responses={
        200: FraisConsultationSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsStaffOrAdmin])
def frais_payer_view(request, pk):
    updated = frais_service.enregistrer_reglement(pk)
    if not updated:
        return Response({"error": f"Frais #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)
    return Response(FraisConsultationSerializer(updated).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Frais de Consultation"],
    summary="Supprimer ou archiver un frais",
    description="Désactive le frais (statut=ANNULE, actif=False) ou le supprime définitivement si hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsStaffOrAdmin])
def frais_delete_view(request, pk):
    hard = request.query_params.get("hard", "false").lower() == "true"
    success = frais_service.supprimer_frais(pk, hard=hard)
    if not success:
        return Response({"error": f"Frais #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Frais #{pk} supprimé définitivement." if hard else f"Frais #{pk} archivé (annulé)."
    return Response({"message": msg}, status=status.HTTP_200_OK)
