import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin
from config.schema_helpers import (
    ErrorResponseSerializer,
    MessageResponseSerializer,
    PAGINATION_PARAMS,
    SEARCH_PARAM,
)
from .sejourSerializers import (
    SejourCreateSerializer,
    SejourReadSerializer,
    SejourSortieSerializer,
    DemandeAnalyseSerializer,
)
from .sejourServices import SejourService

logger = logging.getLogger(__name__)
sejour_service = SejourService()


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Lister ou enregistrer une admission de séjour",
    description="GET: Liste les séjours avec filtres par patient, service, statut, etc.\nPOST: Admet un patient et initialise son parcours.",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="service_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="type_prise_en_charge", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=SejourCreateSerializer,
    responses={
        200: SejourReadSerializer(many=True),
        201: SejourReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def sejour_list_create_view(request):
    if request.method == "GET":
        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = sejour_service.repository.get_all(
            patient_id=request.query_params.get("patient_id"),
            service_id=request.query_params.get("service_id"),
            medecin_id=request.query_params.get("medecin_id"),
            statut=request.query_params.get("statut"),
            type_prise_en_charge=request.query_params.get("type_prise_en_charge"),
            search=request.query_params.get("search"),
            actif_only=actif_only,
        )

        user_role = getattr(request.user, "role", None)
        if user_role == "PATIENT" and hasattr(request.user, "patient"):
            qs = qs.filter(patient=request.user.patient)

        return paginate_response(request, qs, SejourReadSerializer)

    elif request.method == "POST":
        serializer = SejourCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            sejour = sejour_service.admettre_patient(data=serializer.validated_data, user=request.user)
            # Recharger avec relations complètes
            sejour = sejour_service.repository.get_by_id(sejour.id_sejour)
            return Response(SejourReadSerializer(sejour).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error("Erreur d'intégrité admission: %s", e)
            return Response({"detail": "Erreur d'intégrité lors de l'admission."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Détail d'un séjour",
    responses={200: SejourReadSerializer, 404: ErrorResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sejour_detail_view(request, pk: int):
    sejour = sejour_service.repository.get_by_id(pk)
    if not sejour:
        return Response({"detail": "Séjour introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user_role = getattr(request.user, "role", None)
    if user_role == "PATIENT" and hasattr(request.user, "patient"):
        if sejour.patient_id != request.user.patient.id:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

    return Response(SejourReadSerializer(sejour).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Autoriser la sortie médicale d'un patient",
    request=SejourSortieSerializer,
    responses={200: SejourReadSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsMedecinOuAdmin])
def sejour_autoriser_sortie_view(request, pk: int):
    serializer = SejourSortieSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        sejour = sejour_service.autoriser_sortie(
            sejour_id=pk,
            user=request.user,
            motif=serializer.validated_data.get("motif_sortie"),
        )
        return Response(SejourReadSerializer(sejour).data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Clôturer définitivement un séjour (sortie administrative et physique)",
    request=SejourSortieSerializer,
    responses={200: SejourReadSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def sejour_cloturer_view(request, pk: int):
    serializer = SejourSortieSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        sejour = sejour_service.enregistrer_sortie(
            sejour_id=pk,
            user=request.user,
            date_sortie=serializer.validated_data.get("date_sortie"),
            motif_sortie=serializer.validated_data.get("motif_sortie"),
        )
        return Response(SejourReadSerializer(sejour).data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Dossier de synthèse 360° du séjour patient",
    description="Retourne le dossier consolidé du séjour : patient, localisation actuelle, timeline des événements, historique des mouvements et analyses.",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sejour_synthese_view(request, pk: int):
    sejour = sejour_service.repository.get_by_id(pk)
    if not sejour:
        return Response({"detail": "Séjour introuvable."}, status=status.HTTP_404_NOT_FOUND)

    from localisation.localisationSerializers import LocalisationReadSerializer
    from mouvement.mouvementSerializers import MouvementReadSerializer
    from evenement.evenementSerializers import EvenementReadSerializer

    data = {
        "sejour": SejourReadSerializer(sejour).data,
        "localisation_actuelle": LocalisationReadSerializer(sejour.localisation_actuelle).data if sejour.localisation_actuelle else None,
        "historique_localisations": LocalisationReadSerializer(sejour.localisations.all(), many=True).data,
        "mouvements": MouvementReadSerializer(sejour.mouvements.all(), many=True).data,
        "evenements": EvenementReadSerializer(sejour.evenements.all(), many=True).data,
        "analyses": DemandeAnalyseSerializer(sejour.demandes_analyses.all(), many=True).data,
    }
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Séjours & Parcours"],
    summary="Indicateurs statistiques agrégés pour le tableau de bord hospitalier",
    description="Retourne les métriques en direct : patients présents, urgences, hospitalisés, disponibilité des lits et mouvements récents.",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sejour_dashboard_stats_view(request):
    stats = sejour_service.repository.get_statistiques_dashboard()
    return Response(stats, status=status.HTTP_200_OK)
