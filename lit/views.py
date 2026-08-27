from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdmin
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, SEARCH_PARAM
from .litSerializers import LitSerializer
from .litServices import LitService

lit_service = LitService()


# Enregistrement et listing des lits
@extend_schema(
    tags=["Lits"],
    summary="Lister ou créer un lit",
    description="Retourne la liste des lits (GET avec filtres ?chambre_id=, ?etat=, ?search=) ou enregistre un nouveau lit (POST).",
    parameters=[
        OpenApiParameter(name="chambre_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant de chambre."),
        OpenApiParameter(name="etat", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par état du lit."),
        SEARCH_PARAM,
    ],
    request=LitSerializer,
    responses={200: LitSerializer(many=True), 201: LitSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_lit(request):
    if request.method == "GET":
        chambre_id = request.query_params.get('chambre_id') or request.query_params.get('id_chambre')
        etat = request.query_params.get('etat')
        search_q = request.query_params.get('search') or request.query_params.get('q')

        if chambre_id:
            lits = lit_service.get_lits_by_chambre(chambre_id)
        elif etat:
            lits = lit_service.get_lits_by_etat(etat)
        elif search_q:
            lits = lit_service.search_lits(search_q)
        else:
            lits = lit_service.get_all_lits()

        serializer = LitSerializer(lits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["ADMINISTRATEUR"]:
        return Response({"error": "Seul un administrateur peut créer un lit."}, status=status.HTTP_403_FORBIDDEN)

    serializer = LitSerializer(data=request.data)
    if serializer.is_valid():
        try:
            lit = lit_service.create_lit(**serializer.validated_data)
            return Response(LitSerializer(lit).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Erreur lors de la création du lit.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Lits"],
    summary="Lister les lits",
    description="Retourne la liste des lits, avec filtres optionnels (chambre, état, recherche).",
    parameters=[
        OpenApiParameter(name="chambre_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant de chambre (alias : id_chambre)."),
        OpenApiParameter(name="etat", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par état du lit."),
        SEARCH_PARAM,
    ],
    responses={200: LitSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_lits(request):
    chambre_id = request.query_params.get('chambre_id') or request.query_params.get('id_chambre')
    etat = request.query_params.get('etat')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if chambre_id:
        lits = lit_service.get_lits_by_chambre(chambre_id)
    elif etat:
        lits = lit_service.get_lits_by_etat(etat)
    elif search_q:
        lits = lit_service.search_lits(search_q)
    else:
        lits = lit_service.get_all_lits()

    serializer = LitSerializer(lits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Lits"],
    summary="Lister les lits par état",
    description="Retourne les lits correspondant à l'état donné.",
    responses={200: LitSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lits_by_etat(request, etat):
    lits = lit_service.get_lits_by_etat(etat)
    serializer = LitSerializer(lits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Récupérer, modifier ou supprimer un lit grâce à son ID
@extend_schema(
    tags=["Lits"],
    summary="Récupérer, modifier ou supprimer un lit",
    description="Retourne, modifie ou supprime un lit à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=LitSerializer,
    responses={200: LitSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_lit(request, lit_id):
    if request.method in ["PUT", "PATCH"]:
        return update_lit(request, lit_id)
    elif request.method == "DELETE":
        return delete_lit(request, lit_id)

    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(LitSerializer(lit).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Lits"],
    summary="Modifier un lit",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) un lit.",
    request=LitSerializer,
    responses={200: LitSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAdmin])
def update_lit(request, lit_id):
    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = LitSerializer(lit, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = lit_service.update_lit(lit, **serializer.validated_data)
            return Response(LitSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Erreur lors de la modification.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Lits"],
    summary="Supprimer / désactiver un lit",
    description="Marque le lit comme hors service (soft delete), ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_lit(request, lit_id):
    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    lit_service.delete_lit(lit, hard=hard)

    if hard:
        return Response({"message": "Lit supprimé définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Lit marqué comme hors service (archivé) avec succès."}, status=status.HTTP_200_OK)
