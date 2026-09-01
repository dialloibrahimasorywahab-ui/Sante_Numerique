import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .rendezvousSerializers import RendezVousSerializer
from .rendezvousServices import ConflictError, RendezVousService

rendezvous_service = RendezVousService()


def _rendezvous_action_response(message_example):
    """Sérialiseur de réponse commun aux actions confirmer/annuler/terminer."""
    return inline_serializer(
        name=f"RendezVousAction_{message_example}",
        fields={
            "message": serializers.CharField(),
            "rendezvous": RendezVousSerializer(),
        },
    )


@extend_schema(
    tags=["Rendez-vous"],
    summary="Créer un rendez-vous",
    description="Enregistre un nouveau rendez-vous entre un patient et un médecin.",
    request=RendezVousSerializer,
    responses={201: RendezVousSerializer, 400: ErrorResponseSerializer, 409: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_rendezvous(request):
    serializer = RendezVousSerializer(data=request.data)
    if serializer.is_valid():
        try:
            rdv = rendezvous_service.create_rendezvous(**serializer.validated_data)
            return Response(RendezVousSerializer(rdv).data, status=status.HTTP_201_CREATED)
        except ConflictError as e:
            return Response({"error": "Conflit de rendez-vous.", "detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": "Données de rendez-vous invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"error": "Conflit de rendez-vous.", "detail": "Un rendez-vous existe déjà pour ce médecin à cette date et heure."}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            logger.exception("Erreur inattendue lors de la création du rendez-vous: %s", str(e))
            return Response({"error": "Erreur interne lors de la création du rendez-vous."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# recuperation de tous les rendez-vous
@extend_schema(
    tags=["Rendez-vous"],
    summary="Lister les rendez-vous",
    description="Retourne la liste des rendez-vous, avec filtres optionnels (patient, médecin, statut, date, recherche).",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant patient (alias : id_patient)."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par identifiant médecin (alias : id_medecin)."),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par statut du rendez-vous."),
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par date du rendez-vous (alias : date_rdv)."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    responses={200: RendezVousSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_all_rendezvous(request):
    patient_id = request.query_params.get('patient_id') or request.query_params.get('id_patient')
    medecin_id = request.query_params.get('medecin_id') or request.query_params.get('id_medecin')
    statut = request.query_params.get('statut')
    date_rdv = request.query_params.get('date') or request.query_params.get('date_rdv')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if patient_id:
        rdvs = rendezvous_service.get_rendezvous_by_patient(patient_id)
    elif medecin_id:
        rdvs = rendezvous_service.get_rendezvous_by_medecin(medecin_id)
    elif statut:
        rdvs = rendezvous_service.get_rendezvous_by_statut(statut)
    elif date_rdv:
        rdvs = rendezvous_service.get_rendezvous_by_date(date_rdv)
    elif search_q:
        rdvs = rendezvous_service.search_rendezvous(search_q)
    else:
        rdvs = rendezvous_service.get_all_rendezvous()

    return paginate_response(rdvs, request, RendezVousSerializer)

# recuperer un rendez-vous par son statut
@extend_schema(
    tags=["Rendez-vous"],
    summary="Lister les rendez-vous par statut",
    description="Retourne les rendez-vous correspondant au statut donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: RendezVousSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_rendezvous_by_statut(request, statut):
    rdvs = rendezvous_service.get_rendezvous_by_statut(statut)
    return paginate_response(rdvs, request, RendezVousSerializer)

# recuperer un rendez-vous par patient

@extend_schema(
    tags=["Rendez-vous"],
    summary="Lister les rendez-vous d'un patient",
    description="Retourne les rendez-vous rattachés au patient donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: RendezVousSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_rendezvous_by_patient(request, patient_id):
    rdvs = rendezvous_service.get_rendezvous_by_patient(patient_id)
    return paginate_response(rdvs, request, RendezVousSerializer)

# recuperer les rendez-vous d'un medecin
@extend_schema(
    tags=["Rendez-vous"],
    summary="Lister les rendez-vous d'un médecin",
    description="Retourne les rendez-vous rattachés au médecin donné.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: RendezVousSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_rendezvous_by_medecin(request, medecin_id):
    rdvs = rendezvous_service.get_rendezvous_by_medecin(medecin_id)
    return paginate_response(rdvs, request, RendezVousSerializer)

# recuperer un rendez-vous par son id

@extend_schema(
    tags=["Rendez-vous"],
    summary="Récupérer un rendez-vous",
    description="Retourne un rendez-vous à partir de son identifiant.",
    responses={200: RendezVousSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)
    deny_unless_owner_or_staff(request, rdv)
    return Response(RendezVousSerializer(rdv).data, status=status.HTTP_200_OK)

# mettre à jour les données d'un rendez-vous
@extend_schema(
    tags=["Rendez-vous"],
    summary="Modifier un rendez-vous",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) un rendez-vous.",
    request=RendezVousSerializer,
    responses={200: RendezVousSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, rdv)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = RendezVousSerializer(rdv, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = rendezvous_service.update_rendezvous(rdv, **serializer.validated_data)
            return Response(RendezVousSerializer(updated).data, status=status.HTTP_200_OK)
        except (ConflictError, ValueError) as e:
            return Response({"error": "Données de modification invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"error": "Conflit lors de la modification.", "detail": "Un rendez-vous existe déjà avec ces paramètres."}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            logger.exception("Erreur inattendue lors de la modification du rendez-vous: %s", str(e))
            return Response({"error": "Erreur interne lors de la modification du rendez-vous."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Rendez-vous"],
    summary="Confirmer un rendez-vous",
    description="Passe le statut du rendez-vous à CONFIRME. Aucun corps de requête requis.",
    request=None,
    responses={200: _rendezvous_action_response("confirme"), 404: MessageResponseSerializer},
)
@api_view(["PATCH", "POST"])
@permission_classes([IsStaffOrAdmin])
def confirmer_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    updated = rendezvous_service.update_rendezvous(rdv, statut="CONFIRME")
    return Response(
        {"message": "Rendez-vous confirmé avec succès.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=["Rendez-vous"],
    summary="Annuler un rendez-vous",
    description="Passe le statut du rendez-vous à ANNULE. Aucun corps de requête requis.",
    request=None,
    responses={200: _rendezvous_action_response("annule"), 404: MessageResponseSerializer},
)
@api_view(["PATCH", "POST"])
@permission_classes([IsAuthenticated])
def annuler_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, rdv)

    updated = rendezvous_service.update_rendezvous(rdv, statut="ANNULE")
    return Response(
        {"message": "Rendez-vous annulé.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=["Rendez-vous"],
    summary="Terminer un rendez-vous",
    description="Passe le statut du rendez-vous à TERMINE. Aucun corps de requête requis.",
    request=None,
    responses={200: _rendezvous_action_response("termine"), 404: MessageResponseSerializer},
)
@api_view(["PATCH", "POST"])
@permission_classes([IsStaffOrAdmin])
def terminer_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    updated = rendezvous_service.update_rendezvous(rdv, statut="TERMINE")
    return Response(
        {"message": "Rendez-vous marqué comme terminé.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=["Rendez-vous"],
    summary="Supprimer / annuler un rendez-vous",
    description="Annule (soft delete) le rendez-vous, ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsStaffOrAdmin])
def delete_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    rendezvous_service.delete_rendezvous(rdv, hard=hard)

    if hard:
        return Response({"message": "Rendez-vous supprimé définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Rendez-vous annulé (archivé) avec succès."}, status=status.HTTP_200_OK)

