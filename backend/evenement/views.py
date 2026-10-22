import logging
from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsStaffOrAdmin
from config.schema_helpers import ErrorResponseSerializer, PAGINATION_PARAMS
from .evenementSerializers import EvenementCreateSerializer, EvenementReadSerializer
from .evenementServices import EvenementService

logger = logging.getLogger(__name__)
evenement_service = EvenementService()


@extend_schema(
    tags=["Timeline & Événements"],
    summary="Lister ou consigner un événement dans le parcours",
    parameters=[
        OpenApiParameter(name="sejour_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="type_evenement", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="importance", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        *PAGINATION_PARAMS,
    ],
    request=EvenementCreateSerializer,
    responses={
        200: EvenementReadSerializer(many=True),
        201: EvenementReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def evenement_list_create_view(request):
    if request.method == "GET":
        qs = evenement_service.repository.get_all(
            sejour_id=request.query_params.get("sejour_id"),
            type_evenement=request.query_params.get("type_evenement"),
            importance=request.query_params.get("importance"),
        )
        return paginate_response(request, qs, EvenementReadSerializer)

    elif request.method == "POST":
        serializer = EvenementCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            event = evenement_service.enregistrer_evenement(
                sejour_id=serializer.validated_data.get("sejour"),
                data=serializer.validated_data,
                user=request.user,
            )
            event = evenement_service.repository.get_by_id(event.id)
            return Response(EvenementReadSerializer(event).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Timeline & Événements"],
    summary="Détail d'un événement",
    responses={200: EvenementReadSerializer, 404: ErrorResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def evenement_detail_view(request, pk: int):
    event = evenement_service.repository.get_by_id(pk)
    if not event:
        return Response({"detail": "Événement introuvable."}, status=status.HTTP_404_NOT_FOUND)
    return Response(EvenementReadSerializer(event).data, status=status.HTTP_200_OK)
