from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    PAGINATION_PARAMS,
    SEARCH_PARAM,
)
from .consultationSerializers import ConsultationReadSerializer, ConsultationSerializer
from .consultationServices import ConsultationService

consultation_service = ConsultationService()


# Enregistrement et listing des consultations
@extend_schema(
    tags=["Consultation"],
    summary="Lister ou créer une consultation",
    description="GET: Liste l'ensemble des consultations médicales avec filtres (patient, médecin, rdv, all).\nPOST: Enregistre un acte de consultation.",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant patient."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant médecin."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les consultations inactives si true."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=ConsultationSerializer,
    responses={
        200: ConsultationReadSerializer(many=True),
        201: ConsultationReadSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def consultation_list_create_view(request):
    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        # 1. INFIRMIER : pas de liste globale
        if user_role == "INFIRMIER":
            return Response(
                {"error": "Accès refusé. Les infirmiers ne peuvent pas lister toutes les consultations. Veuillez consulter une consultation spécifique par son identifiant."},
                status=status.HTTP_403_FORBIDDEN
            )

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = consultation_service.repository.get_all_consultations(actif_only=actif_only)

        # 2. Filtrage selon le rôle
        if user_role == "ADMINISTRATEUR":
            pass  # L'administrateur a accès à l'ensemble
        elif user_role == "MEDECIN":
            qs = qs.filter(medecin__idUtilisateur=request.user)
        elif user_role == "PATIENT":
            qs = qs.filter(patient__idUtilisateur=request.user)
        else:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        # Filtres optionnels
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

        return paginate_response(qs, request, ConsultationReadSerializer)

    elif request.method == "POST":
        # Seuls les médecins et administrateurs peuvent enregistrer une consultation
        if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response(
                {"error": "Seul un médecin ou administrateur peut enregistrer une consultation."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ConsultationSerializer(data=request.data)
        if serializer.is_valid():
            medecin = serializer.validated_data.get("medecin")

            # Un médecin ne peut enregistrer une consultation que pour lui-même
            if user_role == "MEDECIN":
                if not medecin or medecin.idUtilisateur != request.user:
                    return Response(
                        {"error": "Accès refusé. Vous ne pouvez enregistrer une consultation que pour vous-même en tant que médecin consultant."},
                        status=status.HTTP_403_FORBIDDEN
                    )

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
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def consultation_detail_view(request, pk):
    cons = consultation_service.repository.get_consultation_by_id(pk)
    if not cons:
        return Response({"error": f"Consultation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        # Contrôle d'accès en lecture
        if user_role == "ADMINISTRATEUR" or user_role == "INFIRMIER":
            pass  # Admin et Infirmier peuvent consulter une consultation précise par ID
        elif user_role == "MEDECIN":
            if not cons.medecin or cons.medecin.idUtilisateur != request.user:
                return Response(
                    {"error": "Accès refusé. Vous ne pouvez consulter que vos propres consultations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user_role == "PATIENT":
            if not cons.patient or cons.patient.idUtilisateur != request.user:
                return Response(
                    {"error": "Accès refusé. Vous ne pouvez consulter que vos propres consultations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        return Response(ConsultationReadSerializer(cons).data, status=status.HTTP_200_OK)

    # Modification (PUT / PATCH)
    if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response(
            {"error": "Seul un médecin ou administrateur peut modifier une consultation."},
            status=status.HTTP_403_FORBIDDEN
        )

    if user_role == "MEDECIN":
        if not cons.medecin or cons.medecin.idUtilisateur != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez modifier que vos propres consultations."},
                status=status.HTTP_403_FORBIDDEN
            )

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
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def consultation_delete_view(request, pk):
    cons = consultation_service.repository.get_consultation_by_id(pk)
    if not cons:
        return Response({"error": f"Consultation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(request.user, "role", None)

    if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response(
            {"error": "Seul un médecin ou administrateur peut supprimer une consultation."},
            status=status.HTTP_403_FORBIDDEN
        )

    if user_role == "MEDECIN":
        if not cons.medecin or cons.medecin.idUtilisateur != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez supprimer que vos propres consultations."},
                status=status.HTTP_403_FORBIDDEN
            )

    hard = request.query_params.get("hard", "false").lower() == "true"
    success = consultation_service.supprimer_consultation(pk, hard=hard)
    if not success:
        return Response({"error": f"Consultation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Consultation #{pk} supprimée définitivement." if hard else f"Consultation #{pk} archivée."
    return Response({"message": msg}, status=status.HTTP_200_OK)

