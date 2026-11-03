import logging
from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import (
    IsAuthenticatedReadOnly_IsStaffOrAdminWrite,
    IsStaffOrAdmin,
    ensure_can_access_sejour,
    scope_to_accessible_sejours,
)
from config.schema_helpers import ErrorResponseSerializer, PAGINATION_PARAMS
from .localisationSerializers import LocalisationCreateSerializer, LocalisationReadSerializer
from .localisationServices import LocalisationService

logger = logging.getLogger(__name__)
localisation_service = LocalisationService()


@extend_schema(
    tags=["Localisation & Lits"],
    summary="Lister ou affecter une localisation patient",
    parameters=[
        OpenApiParameter(name="sejour_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="service_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="chambre_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="lit_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="est_actuelle", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False),
        *PAGINATION_PARAMS,
    ],
    request=LocalisationCreateSerializer,
    responses={
        200: LocalisationReadSerializer(many=True),
        201: LocalisationReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedReadOnly_IsStaffOrAdminWrite])
def localisation_list_create_view(request):
    if request.method == "GET":
        est_actuelle_param = request.query_params.get("est_actuelle")
        est_actuelle = None
        if est_actuelle_param is not None:
            est_actuelle = est_actuelle_param.lower() == "true"

        qs = localisation_service.repository.get_all(
            sejour_id=request.query_params.get("sejour_id"),
            service_id=request.query_params.get("service_id"),
            chambre_id=request.query_params.get("chambre_id"),
            lit_id=request.query_params.get("lit_id"),
            est_actuelle=est_actuelle,
        )
        qs = scope_to_accessible_sejours(request, qs)
        return paginate_response(request, qs, LocalisationReadSerializer)

    elif request.method == "POST":
        serializer = LocalisationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            loc = localisation_service.affecter_localisation(
                sejour_id=serializer.validated_data.get("sejour"),
                data=serializer.validated_data,
                user=request.user,
            )
            loc = localisation_service.repository.get_by_id(loc.id)
            return Response(LocalisationReadSerializer(loc).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Localisation & Lits"],
    summary="Détail d'une localisation",
    responses={200: LocalisationReadSerializer, 404: ErrorResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def localisation_detail_view(request, pk: int):
    loc = localisation_service.repository.get_by_id(pk)
    if not loc:
        return Response({"detail": "Localisation introuvable."}, status=status.HTTP_404_NOT_FOUND)
    ensure_can_access_sejour(request, loc.sejour)
    return Response(LocalisationReadSerializer(loc).data, status=status.HTTP_200_OK)
