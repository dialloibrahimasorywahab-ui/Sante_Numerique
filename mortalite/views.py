from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, SEARCH_PARAM
from .mortaliteSerializers import MortaliteSerializer
from .mortaliteServices import MortaliteService

mortalite_service = MortaliteService()


@extend_schema(
    tags=["Mortalité"],
    summary="Créer une fiche de décès",
    description="Enregistre une nouvelle fiche de décès.",
    request=MortaliteSerializer,
    responses={201: MortaliteSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
def create_deces(request):
    serializer = MortaliteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            deces = mortalite_service.create_deces(**serializer.validated_data)
            return Response(
                MortaliteSerializer(deces).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la création de la fiche de décès", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Mortalité"],
    summary="Lister les fiches de décès",
    description="Retourne la liste des fiches de décès, avec filtres optionnels (patient, médecin, date, recherche).",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant patient (alias : id_patient)."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant médecin (alias : id_medecin)."),
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par date de décès (alias : date_deces)."),
        SEARCH_PARAM,
    ],
    responses={200: MortaliteSerializer(many=True)},
)
@api_view(["GET"])
def get_all_mortalite(request):
    patient_id = request.query_params.get('patient_id') or request.query_params.get('id_patient')
    medecin_id = request.query_params.get('medecin_id') or request.query_params.get('id_medecin')
    date_deces = request.query_params.get('date') or request.query_params.get('date_deces')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if patient_id:
        mortalites = mortalite_service.get_mortalites_by_patient(patient_id)
    elif medecin_id:
        mortalites = mortalite_service.get_mortalites_by_medecin(medecin_id)
    elif date_deces:
        mortalites = mortalite_service.get_mortalites_by_date(date_deces)
    elif search_q:
        mortalites = mortalite_service.search_mortalites(search_q)
    else:
        mortalites = mortalite_service.get_all_mortalites()

    serializer = MortaliteSerializer(mortalites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Mortalité"],
    summary="Récupérer une fiche de décès",
    description="Retourne une fiche de décès à partir de son identifiant.",
    responses={200: MortaliteSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET"])
def get_mortalite(request, id_deces):
    deces = mortalite_service.get_deces_by_id(id_deces)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(MortaliteSerializer(deces).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Mortalité"],
    summary="Modifier une fiche de décès",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) une fiche de décès.",
    request=MortaliteSerializer,
    responses={200: MortaliteSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
def update_mortalite(request, deces_id):
    deces = mortalite_service.get_deces_by_id(deces_id)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MortaliteSerializer(deces, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = mortalite_service.update_deces(deces, **serializer.validated_data)
            return Response(MortaliteSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la modification", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Mortalité"],
    summary="Supprimer / désactiver une fiche de décès",
    description="Désactive (soft delete) la fiche de décès, ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
def delete_mortalite(request, deces_id):
    deces = mortalite_service.get_deces_by_id(deces_id)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    mortalite_service.delete_deces(deces, hard=hard)

    if hard:
        return Response({"message": "Fiche de décès supprimée définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Fiche de décès désactivée (archivée) avec succès."}, status=status.HTTP_200_OK)
