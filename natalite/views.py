from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .nataliteSerializers import NataliteSerializer
from .nataliteServices import NataliteService

# Instanciation du service de natalite
natalite_service = NataliteService()


# Enregistrer un nouveau-né
@extend_schema(
    tags=["Natalité"],
    summary="Créer une fiche de naissance",
    description="Enregistre un nouveau-né.",
    request=NataliteSerializer,
    responses={201: NataliteSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsMedecinOuAdmin])
def create_naissance(request):
    serializer = NataliteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            natality = natalite_service.create_nouveaune(**serializer.validated_data)
            return Response(
                NataliteSerializer(natality).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Erreur lors de l'enregistrement du nouveau-né", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Récupération de tous les nouveaux-nés avec filtres
@extend_schema(
    tags=["Natalité"],
    summary="Lister les naissances",
    description="Retourne la liste des naissances, avec filtres optionnels (patient, médecin, sexe, date, recherche).",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant de la patiente/mère (alias : id_patient)."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant du médecin superviseur (alias : id_medecin)."),
        OpenApiParameter(name="sexe", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par sexe du nouveau-né."),
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par date de naissance (alias : date_naissance)."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    responses={200: NataliteSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_all_natality(request):
    patient_id = request.query_params.get('patient_id') or request.query_params.get('id_patient')
    medecin_id = request.query_params.get('medecin_id') or request.query_params.get('id_medecin')
    sexe = request.query_params.get('sexe')
    date_naissance = request.query_params.get('date') or request.query_params.get('date_naissance')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if patient_id:
        natalities = natalite_service.get_nouveaux_nes_by_patient(patient_id)
    elif medecin_id:
        natalities = natalite_service.get_nouveaux_nes_by_medecin(medecin_id)
    elif sexe:
        natalities = natalite_service.get_natalities_by_sexe(sexe)
    elif date_naissance:
        natalities = natalite_service.get_nouveaux_nes_by_date(date_naissance)
    elif search_q:
        natalities = natalite_service.search_nouveaux_nes(search_q)
    else:
        natalities = natalite_service.get_all_nouveau_ne()

    return paginate_response(natalities, request, NataliteSerializer)


# Récupérer les nouveaux-nés par leur sexe
@extend_schema(
    tags=["Natalité"],
    summary="Lister les naissances par sexe",
    description="Retourne les naissances correspondant au sexe donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: NataliteSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_natalities_by_sexe(request, sexe):
    natalities = natalite_service.get_natalities_by_sexe(sexe)
    return paginate_response(natalities, request, NataliteSerializer)


# Afficher les nouveaux-nés d'une patiente (mère)
@extend_schema(
    tags=["Natalité"],
    summary="Lister les naissances d'une patiente",
    description="Retourne les naissances rattachées à la patiente (mère) donnée.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: NataliteSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_natalities_by_patient(request, patient_id):
    natalities = natalite_service.get_nouveaux_nes_by_patient(patient_id)
    return paginate_response(natalities, request, NataliteSerializer)


# Afficher les nouveaux-nés d'un médecin superviseur
@extend_schema(
    tags=["Natalité"],
    summary="Lister les naissances supervisées par un médecin",
    description="Retourne les naissances rattachées au médecin superviseur donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: NataliteSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_natalities_by_medecin(request, medecin_id):
    natalities = natalite_service.get_nouveaux_nes_by_medecin(medecin_id)
    return paginate_response(natalities, request, NataliteSerializer)


# Afficher un nouveau-né par son ID
@extend_schema(
    tags=["Natalité"],
    summary="Récupérer une fiche de naissance",
    description="Retourne une fiche de naissance à partir de son identifiant.",
    responses={200: NataliteSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_natality(request, id_natality):
    natality = natalite_service.get_nouveauneById(id_natality)
    if natality is None:
        return Response({"message": "Aucune natalité correspondante"}, status=status.HTTP_404_NOT_FOUND)
    deny_unless_owner_or_staff(request, natality)
    return Response(NataliteSerializer(natality).data, status=status.HTTP_200_OK)


# Mettre à jour les informations d'un nouveau-né
@extend_schema(
    tags=["Natalité"],
    summary="Modifier une fiche de naissance",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) une fiche de naissance.",
    request=NataliteSerializer,
    responses={200: NataliteSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsMedecinOuAdmin])
def update_natality(request, natality_id):
    natality = natalite_service.get_nouveauneById(natality_id)
    if natality is None:
        return Response({"message": "Aucune natalité trouvée"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = NataliteSerializer(natality, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = natalite_service.update_data_nouveau_ne(natality, **serializer.validated_data)
            return Response(NataliteSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la modification de la natalité", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Désactiver (soft delete) ou supprimer une fiche de natalité
@extend_schema(
    tags=["Natalité"],
    summary="Supprimer / désactiver une fiche de naissance",
    description="Désactive (soft delete) la fiche de naissance, ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsMedecinOuAdmin])
def delete_natality(request, natality_id):
    natality = natalite_service.get_nouveauneById(natality_id)
    if natality is None:
        return Response({"message": "Aucune natalité trouvée"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    natalite_service.delete_nouveau_ne(natality, hard=hard)

    if hard:
        return Response({"message": "Fiche de natalité supprimée définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Fiche de natalité désactivée (archivée) avec succès."}, status=status.HTTP_200_OK)
