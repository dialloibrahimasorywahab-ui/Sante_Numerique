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
from .consultationSerializers import ConsultationReadSerializer, ConsultationSerializer
from .consultationServices import ConsultationService

consultation_service = ConsultationService()


@extend_schema(
    tags=["Consultation"],
    summary="Lister ou créer une consultation",
    description="GET: Liste l'ensemble des consultations médicales avec filtres (patient, médecin, rdv, all).\nPOST: Enregistre un acte de consultation.",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant patient."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant médecin."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les consultations inactives si true."),
        SEARCH_PARAM,
    ],
    request=ConsultationSerializer,
    responses={
        200: ConsultationReadSerializer(many=True),
        201: ConsultationReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def consultation_list_create_view(request):
    if request.method == "GET":
        if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
            return Response({"error": "Accès réservé au personnel soignant et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = consultation_service.repository.get_all_consultations(actif_only=actif_only)

        patient_id = request.query_params.get("patient_id") or request.query_params.get("id_patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        medecin_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
        if medecin_id:
            qs = qs.filter(medecin_id=medecin_id)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(
                patient__idUtilisateur__nom__icontains=search
            ) | qs.filter(
                patient__idUtilisateur__prenom__icontains=search
            ) | qs.filter(
                diagnostic__icontains=search
            )

        serializer = ConsultationReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Seul un médecin ou administrateur peut enregistrer une consultation."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ConsultationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                cons = consultation_service.creer_consultation(**serializer.validated_data)
                return Response(ConsultationReadSerializer(cons).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Consultation"],
    summary="Détail ou mise à jour d'une consultation",
    description="Accède aux détails d'une consultation médicale ou met à jour le compte-rendu.",
    request=ConsultationSerializer,
    responses={
        200: ConsultationReadSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def consultation_detail_view(request, pk):
    cons = consultation_service.repository.get_consultation_by_id(pk)
    if not cons:
        return Response({"error": f"Consultation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, cons)

    if request.method == "GET":
        return Response(ConsultationReadSerializer(cons).data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response({"error": "Seul un médecin ou administrateur peut modifier une consultation."}, status=status.HTTP_403_FORBIDDEN)

    partial = (request.method == "PATCH")
    serializer = ConsultationSerializer(cons, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = consultation_service.mettre_a_jour_consultation(pk, **serializer.validated_data)
            return Response(ConsultationReadSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Consultation"],
    summary="Supprimer ou archiver une consultation",
    description="Désactive la consultation (actif=False) ou la supprime définitivement si hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsMedecinOuAdmin])
def consultation_delete_view(request, pk):
    hard = request.query_params.get("hard", "false").lower() == "true"
    success = consultation_service.supprimer_consultation(pk, hard=hard)
    if not success:
        return Response({"error": f"Consultation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Consultation #{pk} supprimée définitivement." if hard else f"Consultation #{pk} archivée."
    return Response({"message": msg}, status=status.HTTP_200_OK)
