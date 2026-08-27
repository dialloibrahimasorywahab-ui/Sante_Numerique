from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    SEARCH_PARAM,
)
from .ordonnanceSerializers import OrdonnanceReadSerializer, OrdonnanceSerializer
from .ordonnanceServices import OrdonnanceService

ordonnance_service = OrdonnanceService()


@extend_schema(
    tags=["Ordonnance"],
    summary="Lister ou prescrire une ordonnance",
    description="GET: Liste les ordonnances de prescription médicale avec filtres (consultation, reference, search, all).\nPOST: Crée une nouvelle ordonnance.",
    parameters=[
        OpenApiParameter(name="consultation_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant consultation."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les ordonnances inactives si true."),
        SEARCH_PARAM,
    ],
    request=OrdonnanceSerializer,
    responses={
        200: OrdonnanceReadSerializer(many=True),
        201: OrdonnanceReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def ordonnance_list_create_view(request):
    if request.method == "GET":
        if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
            return Response({"error": "Accès réservé au personnel soignant et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = ordonnance_service.repository.get_all_ordonnances(actif_only=actif_only)

        consultation_id = request.query_params.get("consultation_id") or request.query_params.get("id_consultation")
        if consultation_id:
            qs = qs.filter(consultation_id=consultation_id)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(reference__icontains=search) | qs.filter(observation__icontains=search)

        serializer = OrdonnanceReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Seul un médecin ou administrateur peut prescrire une ordonnance."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrdonnanceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ord_obj = ordonnance_service.prescrire_ordonnance(**serializer.validated_data)
                return Response(OrdonnanceReadSerializer(ord_obj).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Ordonnance"],
    summary="Détail ou mise à jour d'une ordonnance",
    description="Accède aux détails d'une ordonnance ou met à jour la prescription.",
    request=OrdonnanceSerializer,
    responses={
        200: OrdonnanceReadSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def ordonnance_detail_view(request, pk):
    ord_obj = ordonnance_service.repository.get_ordonnance_by_id(pk)
    if not ord_obj:
        return Response({"error": f"Ordonnance #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, ord_obj)

    if request.method == "GET":
        return Response(OrdonnanceReadSerializer(ord_obj).data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response({"error": "Seul un médecin ou administrateur peut modifier une ordonnance."}, status=status.HTTP_403_FORBIDDEN)

    partial = (request.method == "PATCH")
    serializer = OrdonnanceSerializer(ord_obj, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = ordonnance_service.mettre_a_jour_ordonnance(pk, **serializer.validated_data)
            return Response(OrdonnanceReadSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Ordonnance"],
    summary="Supprimer ou archiver une ordonnance",
    description="Désactive l'ordonnance (actif=False) ou la supprime définitivement si hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsMedecinOuAdmin])
def ordonnance_delete_view(request, pk):
    hard = request.query_params.get("hard", "false").lower() == "true"
    success = ordonnance_service.supprimer_ordonnance(pk, hard=hard)
    if not success:
        return Response({"error": f"Ordonnance #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Ordonnance #{pk} supprimée définitivement." if hard else f"Ordonnance #{pk} archivée."
    return Response({"message": msg}, status=status.HTTP_200_OK)
