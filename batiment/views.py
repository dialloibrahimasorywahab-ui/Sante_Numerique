from django.db import IntegrityError
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdmin, IsStaffOrAdmin
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, SEARCH_PARAM
from .batimentSerializers import BatimentSerializer
from .batimentServices import BatimentService
from chambre.chambreSerializers import ChambreSerializer

batiment_service = BatimentService()


# Enregistrement et listing des bâtiments
@extend_schema(
    tags=["Bâtiments"],
    summary="Lister ou créer un bâtiment",
    description="Retourne la liste des bâtiments (GET avec ?search= optionnel) ou enregistre un nouveau bâtiment (POST).",
    parameters=[SEARCH_PARAM],
    request=BatimentSerializer,
    responses={200: BatimentSerializer(many=True), 201: BatimentSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_batiment(request):
    if request.method == "GET":
        query = request.query_params.get("search") or request.query_params.get("q")
        if query:
            batiments = batiment_service.search_batiments(query)
        else:
            batiments = batiment_service.get_all_batiments()
        serializer = BatimentSerializer(batiments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["ADMINISTRATEUR"]:
        return Response({"error": "Seul un administrateur peut créer un bâtiment."}, status=status.HTTP_403_FORBIDDEN)

    serializer = BatimentSerializer(data=request.data)
    if serializer.is_valid():
        try:
            batiment = batiment_service.create_batiment(**serializer.validated_data)
            return Response(BatimentSerializer(batiment).data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"error": "Un bâtiment avec ce nom existe déjà.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Bâtiments"],
    summary="Lister les bâtiments",
    description="Retourne la liste des bâtiments, avec recherche libre optionnelle.",
    parameters=[SEARCH_PARAM],
    responses={200: BatimentSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_batiments(request):
    query = request.query_params.get("search") or request.query_params.get("q")
    if query:
        batiments = batiment_service.search_batiments(query)
    else:
        batiments = batiment_service.get_all_batiments()
    serializer = BatimentSerializer(batiments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Récupérer, modifier ou supprimer un bâtiment grâce à son ID
@extend_schema(
    tags=["Bâtiments"],
    summary="Récupérer, modifier ou supprimer un bâtiment",
    description="Retourne, modifie ou supprime un bâtiment à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=BatimentSerializer,
    responses={200: BatimentSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_batiment(request, batiment_id):
    if request.method in ["PUT", "PATCH"]:
        return update_batiment(request, batiment_id)
    elif request.method == "DELETE":
        return delete_batiment(request, batiment_id)

    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(BatimentSerializer(batiment).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Bâtiments"],
    summary="Lister les chambres d'un bâtiment",
    description="Retourne le bâtiment ainsi que la liste de ses chambres et leur total.",
    responses={
        200: inline_serializer(
            name="BatimentChambresResponse",
            fields={
                "batiment": BatimentSerializer(),
                "chambres": ChambreSerializer(many=True),
                "total_chambres": serializers.IntegerField(),
            },
        ),
        404: MessageResponseSerializer,
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_batiment_chambres(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)

    chambres = batiment.chambres.all()
    serializer = ChambreSerializer(chambres, many=True)
    return Response(
        {
            "batiment": BatimentSerializer(batiment).data,
            "chambres": serializer.data,
            "total_chambres": chambres.count()
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=["Bâtiments"],
    summary="Modifier un bâtiment",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) un bâtiment.",
    request=BatimentSerializer,
    responses={200: BatimentSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
    examples=[
        OpenApiExample(
            name="Modification partielle / complète",
            value={
                "nom": "Bâtiment Principal Modifié",
                "description": "Nouvelle description",
                "nombre_chambre": None,
                "actif": True
            },
            request_only=True,
        )
    ]
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAdmin])
def update_batiment(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = BatimentSerializer(batiment, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = batiment_service.update_batiment(batiment, **serializer.validated_data)
            return Response(BatimentSerializer(updated).data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": "Erreur d'intégrité.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Bâtiments"],
    summary="Supprimer / désactiver un bâtiment",
    description="Désactive (soft delete) le bâtiment, ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_batiment(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    batiment_service.delete_batiment(batiment, hard=hard)

    if hard:
        return Response({"message": "Bâtiment supprimé définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Bâtiment désactivé (archivé) avec succès."}, status=status.HTTP_200_OK)
