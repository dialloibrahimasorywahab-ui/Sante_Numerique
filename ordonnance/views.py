import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes

logger = logging.getLogger(__name__)
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
from .ordonnanceSerializers import OrdonnanceReadSerializer, OrdonnanceSerializer
from .ordonnanceServices import OrdonnanceService

ordonnance_service = OrdonnanceService()


# Enregistrement et listing des ordonnances
@extend_schema(
    tags=["Ordonnance"],
    summary="Lister ou prescrire une ordonnance",
    description="GET: Liste les ordonnances de prescription médicale avec filtres (consultation, reference, search, all).\nPOST: Crée une nouvelle ordonnance.",
    parameters=[
        OpenApiParameter(name="consultation_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant consultation."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les ordonnances inactives si true."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=OrdonnanceSerializer,
    responses={
        200: OrdonnanceReadSerializer(many=True),
        201: OrdonnanceReadSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def ordonnance_list_create_view(request):
    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        # 1. INFIRMIER : pas de liste globale
        if user_role == "INFIRMIER":
            return Response(
                {"error": "Accès refusé. Les infirmiers ne peuvent pas lister toutes les ordonnances. Veuillez consulter une ordonnance spécifique par son identifiant."},
                status=status.HTTP_403_FORBIDDEN
            )

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = ordonnance_service.repository.get_all_ordonnances(actif_only=actif_only)

        # 2. Filtrage selon le rôle
        if user_role == "ADMINISTRATEUR":
            pass  # L'administrateur a accès à l'ensemble
        elif user_role == "MEDECIN":
            qs = qs.filter(consultation__medecin__idUtilisateur=request.user)
        elif user_role == "PATIENT":
            qs = qs.filter(consultation__patient__idUtilisateur=request.user)
        else:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        # Filtres optionnels
        consultation_id = request.query_params.get("consultation_id") or request.query_params.get("id_consultation")
        if consultation_id:
            qs = qs.filter(consultation_id=consultation_id)

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(reference__icontains=search) | qs.filter(observation__icontains=search)

        return paginate_response(qs, request, OrdonnanceReadSerializer)

    elif request.method == "POST":
        # Seuls les médecins et les administrateurs peuvent prescrire
        if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response(
                {"error": "Seul un médecin ou un administrateur peut prescrire une ordonnance."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrdonnanceSerializer(data=request.data)
        if serializer.is_valid():
            consultation = serializer.validated_data.get("consultation")

            # Un médecin ne peut prescrire que pour ses propres consultations
            if user_role == "MEDECIN":
                if not consultation or not consultation.medecin or consultation.medecin.idUtilisateur != request.user:
                    return Response(
                        {"error": "Accès refusé. Vous ne pouvez prescrire une ordonnance que pour vos propres consultations."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            try:
                ord_obj = ordonnance_service.prescrire_ordonnance(**serializer.validated_data)
                return Response(OrdonnanceReadSerializer(ord_obj).data, status=status.HTTP_201_CREATED)
            except (ValueError, ValidationError, IntegrityError) as e:
                return Response({"error": "Données de prescription invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception("Erreur inattendue lors de la prescription d'ordonnance: %s", str(e))
                return Response({"error": "Erreur interne lors de la prescription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Ordonnance"],
    summary="Détail ou mise à jour d'une ordonnance",
    description="Accède aux détails d'une ordonnance ou met à jour la prescription.",
    request=OrdonnanceSerializer,
    responses={
        200: OrdonnanceReadSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def ordonnance_detail_view(request, pk):
    ord_obj = ordonnance_service.repository.get_ordonnance_by_id(pk)
    if not ord_obj:
        return Response({"error": f"Ordonnance #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        # Contrôle d'accès en lecture
        if user_role == "ADMINISTRATEUR" or user_role == "INFIRMIER":
            pass  # Admin et Infirmier peuvent consulter une ordonnance précise par ID
        elif user_role == "MEDECIN":
            if not ord_obj.consultation or not ord_obj.consultation.medecin or ord_obj.consultation.medecin.idUtilisateur != request.user:
                return Response(
                    {"error": "Accès refusé. Vous ne pouvez consulter que les ordonnances de vos propres consultations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user_role == "PATIENT":
            if not ord_obj.consultation or not ord_obj.consultation.patient or ord_obj.consultation.patient.idUtilisateur != request.user:
                return Response(
                    {"error": "Accès refusé. Vous ne pouvez consulter que vos propres ordonnances."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        return Response(OrdonnanceReadSerializer(ord_obj).data, status=status.HTTP_200_OK)

    # Modification (PUT / PATCH)
    if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response(
            {"error": "Seul un médecin ou un administrateur peut modifier une ordonnance."},
            status=status.HTTP_403_FORBIDDEN
        )

    if user_role == "MEDECIN":
        if not ord_obj.consultation or not ord_obj.consultation.medecin or ord_obj.consultation.medecin.idUtilisateur != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez modifier que les ordonnances de vos propres consultations."},
                status=status.HTTP_403_FORBIDDEN
            )

    partial = (request.method == "PATCH")
    serializer = OrdonnanceSerializer(ord_obj, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = ordonnance_service.mettre_a_jour_ordonnance(pk, **serializer.validated_data)
            return Response(OrdonnanceReadSerializer(updated).data, status=status.HTTP_200_OK)
        except (ValueError, ValidationError, IntegrityError) as e:
            return Response({"error": "Données de modification invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Erreur inattendue lors de la mise à jour d'ordonnance: %s", str(e))
            return Response({"error": "Erreur interne lors de la mise à jour."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Ordonnance"],
    summary="Supprimer ou archiver une ordonnance",
    description="Désactive l'ordonnance (actif=False) ou la supprime définitivement si hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def ordonnance_delete_view(request, pk):
    ord_obj = ordonnance_service.repository.get_ordonnance_by_id(pk)
    if not ord_obj:
        return Response({"error": f"Ordonnance #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(request.user, "role", None)

    if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response(
            {"error": "Seul un médecin ou un administrateur peut supprimer une ordonnance."},
            status=status.HTTP_403_FORBIDDEN
        )

    if user_role == "MEDECIN":
        if not ord_obj.consultation or not ord_obj.consultation.medecin or ord_obj.consultation.medecin.idUtilisateur != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez supprimer que les ordonnances de vos propres consultations."},
                status=status.HTTP_403_FORBIDDEN
            )

    hard = request.query_params.get("hard", "false").lower() == "true"
    success = ordonnance_service.supprimer_ordonnance(pk, hard=hard)
    if not success:
        return Response({"error": f"Ordonnance #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Ordonnance #{pk} supprimée définitivement." if hard else f"Ordonnance #{pk} archivée."
    return Response({"message": msg}, status=status.HTTP_200_OK)

