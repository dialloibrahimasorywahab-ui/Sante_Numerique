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
from .mouvementSerializers import MouvementReadSerializer, MouvementTransfertCreateSerializer
from .mouvementServices import MouvementService

logger = logging.getLogger(__name__)
mouvement_service = MouvementService()


@extend_schema(
    tags=["Mouvements & Transferts"],
    summary="Lister les mouvements de patients",
    parameters=[
        OpenApiParameter(name="sejour_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name="type_mouvement", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        *PAGINATION_PARAMS,
    ],
    responses={200: MouvementReadSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mouvement_list_view(request):
    qs = mouvement_service.repository.get_all(
        sejour_id=request.query_params.get("sejour_id"),
        type_mouvement=request.query_params.get("type_mouvement"),
    )
    return paginate_response(request, qs, MouvementReadSerializer)


@extend_schema(
    tags=["Mouvements & Transferts"],
    summary="Effectuer un transfert de patient",
    description="Transfert physique ou administratif d'un patient vers un nouveau service, chambre ou lit.",
    request=MouvementTransfertCreateSerializer,
    responses={
        201: MouvementReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def mouvement_transfert_view(request):
    serializer = MouvementTransfertCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        mouvement = mouvement_service.effectuer_transfert(
            sejour_id=serializer.validated_data.get("sejour"),
            data=serializer.validated_data,
            user=request.user,
        )
        mouvement = mouvement_service.repository.get_by_id(mouvement.id)
        return Response(MouvementReadSerializer(mouvement).data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response(getattr(e, "message_dict", {"detail": str(e)}), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Mouvements & Transferts"],
    summary="Détail d'un mouvement",
    responses={200: MouvementReadSerializer, 404: ErrorResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mouvement_detail_view(request, pk: int):
    mouvement = mouvement_service.repository.get_by_id(pk)
    if not mouvement:
        return Response({"detail": "Mouvement introuvable."}, status=status.HTTP_404_NOT_FOUND)
    return Response(MouvementReadSerializer(mouvement).data, status=status.HTTP_200_OK)
