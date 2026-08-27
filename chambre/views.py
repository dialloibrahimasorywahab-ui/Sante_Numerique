from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsAdmin
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .chambreSerializers import ChambreSerializer
from .chambreServices import ChambreService

chambre_service = ChambreService()


# Enregistrement et listing des chambres
@extend_schema(
    tags=["Chambres"],
    summary="Lister ou créer une chambre",
    description="Retourne la liste des chambres (GET avec filtres ?batiment_id=, ?type_chambre=, ?statut=, ?search=) ou enregistre une nouvelle chambre (POST).",
    parameters=[
        OpenApiParameter(name="batiment_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant de bâtiment."),
        OpenApiParameter(name="type_chambre", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par type de chambre."),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par statut de la chambre."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=ChambreSerializer,
    responses={200: ChambreSerializer(many=True), 201: ChambreSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_chambre(request):
    if request.method == "GET":
        batiment_id = request.query_params.get('batiment_id') or request.query_params.get('id_batiment')
        type_chambre = request.query_params.get('type_chambre') or request.query_params.get('type')
        statut = request.query_params.get('statut')
        search_q = request.query_params.get('search') or request.query_params.get('q')

        if batiment_id:
            chambres = chambre_service.get_chambres_by_batiment(batiment_id)
        elif type_chambre:
            chambres = chambre_service.get_chambres_by_type(type_chambre)
        elif statut:
            chambres = chambre_service.get_chambres_by_statut(statut)
        elif search_q:
            chambres = chambre_service.search_chambres(search_q)
        else:
            chambres = chambre_service.get_all_chambres()

        return paginate_response(chambres, request, ChambreSerializer)

    if getattr(request.user, "role", None) not in ["ADMINISTRATEUR"]:
        return Response({"error": "Seul un administrateur peut créer une chambre."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ChambreSerializer(data=request.data)
    if serializer.is_valid():
        try:
            chambre = chambre_service.create_chambre(**serializer.validated_data)
            if chambre.batiment:
                chambre.batiment.sync_nombre_chambres()
            return Response(ChambreSerializer(chambre).data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"error": "Une chambre avec ce numéro existe déjà dans ce bâtiment.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Chambres"],
    summary="Lister les chambres",
    description="Retourne la liste des chambres, avec filtres optionnels (bâtiment, type, statut, recherche).",
    parameters=[
        OpenApiParameter(name="batiment_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant de bâtiment (alias : id_batiment)."),
        OpenApiParameter(name="type_chambre", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par type de chambre (alias : type)."),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par statut de la chambre."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    responses={200: ChambreSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_chambres(request):
    batiment_id = request.query_params.get('batiment_id') or request.query_params.get('id_batiment')
    type_chambre = request.query_params.get('type_chambre') or request.query_params.get('type')
    statut = request.query_params.get('statut')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if batiment_id:
        chambres = chambre_service.get_chambres_by_batiment(batiment_id)
    elif type_chambre:
        chambres = chambre_service.get_chambres_by_type(type_chambre)
    elif statut:
        chambres = chambre_service.get_chambres_by_statut(statut)
    elif search_q:
        chambres = chambre_service.search_chambres(search_q)
    else:
        chambres = chambre_service.get_all_chambres()

    return paginate_response(chambres, request, ChambreSerializer)


@extend_schema(
    tags=["Chambres"],
    summary="Lister les chambres par type",
    description="Retourne les chambres correspondant au type donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: ChambreSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chambres_by_type(request, type_chambre):
    chambres = chambre_service.get_chambres_by_type(type_chambre)
    return paginate_response(chambres, request, ChambreSerializer)


@extend_schema(
    tags=["Chambres"],
    summary="Lister les chambres par statut",
    description="Retourne les chambres correspondant au statut donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: ChambreSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chambres_by_statut(request, statut):
    chambres = chambre_service.get_chambres_by_statut(statut)
    return paginate_response(chambres, request, ChambreSerializer)


# Récupérer, modifier ou supprimer une chambre grâce à son ID
@extend_schema(
    tags=["Chambres"],
    summary="Récupérer, modifier ou supprimer une chambre",
    description="Retourne, modifie ou supprime une chambre à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=ChambreSerializer,
    responses={200: ChambreSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_chambre(request, chambre_id):
    if request.method in ["PUT", "PATCH"]:
        return update_chambre(request, chambre_id)
    elif request.method == "DELETE":
        return delete_chambre(request, chambre_id)

    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(ChambreSerializer(chambre).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Chambres"],
    summary="Modifier une chambre",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) une chambre.",
    request=ChambreSerializer,
    responses={200: ChambreSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
    examples=[
        OpenApiExample(
            name="Modification de chambre",
            value={
                "numero_chambre": 0,
                "type_chambre": "INDIVIDUELLE",
                "capacite": 1,
                "statut": "DISPONIBLE"
            },
            request_only=True,
        )
    ]
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAdmin])
def update_chambre(request, chambre_id):
    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = ChambreSerializer(chambre, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = chambre_service.update_chambre(chambre, **serializer.validated_data)
            if updated.batiment:
                updated.batiment.sync_nombre_chambres()
            return Response(ChambreSerializer(updated).data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": "Erreur d'intégrité.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Chambres"],
    summary="Supprimer / désactiver une chambre",
    description="Marque la chambre comme hors service (soft delete), ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_chambre(request, chambre_id):
    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)

    batiment = chambre.batiment
    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    chambre_service.delete_chambre(chambre, hard=hard)
    if batiment:
        batiment.sync_nombre_chambres()

    if hard:
        return Response({"message": "Chambre supprimée définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Chambre marquée comme hors service (archivée) avec succès."}, status=status.HTTP_200_OK)
