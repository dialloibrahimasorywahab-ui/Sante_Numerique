import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .rendezvousSerializers import RendezVousSerializer
from .rendezvousServices import ConflictError, RendezVousService
from .models import RendezVous
from patients.models import Patient
from medecin.models import Medecin
import datetime

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


# Créneau availability endpoint
@extend_schema(
    tags=["Rendez-vous"],
    summary="Obtenir les créneaux disponibles d'un médecin",
    description="Retourne la liste des créneaux horaires (libres vs occupés) pour un médecin et une date donnés.",
    parameters=[
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=True, description="ID du médecin"),
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=False, description="Date au format YYYY-MM-DD (défaut: aujourd'hui)"),
    ],
    responses={200: inline_serializer(
        name="CreneauxResponse",
        fields={
            "medecin_id": serializers.IntegerField(),
            "date": serializers.CharField(),
            "creneaux": serializers.ListField(child=serializers.DictField()),
        }
    )},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_creneaux_disponibles(request):
    medecin_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
    date_str = request.query_params.get("date") or request.query_params.get("date_rdv")

    if not medecin_id:
        return Response({"error": "Le paramètre medecin_id est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        medecin_id = int(medecin_id)
    except (ValueError, TypeError):
        return Response({"error": "Identifiant médecin invalide."}, status=status.HTTP_400_BAD_REQUEST)

    today = datetime.date.today()
    target_date = today
    if date_str:
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Format de date invalide. Utilisez YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    if target_date < today:
        return Response({"error": "Impossible de consulter des créneaux dans le passé."}, status=status.HTTP_400_BAD_REQUEST)

    # Standard clinical consultation slots
    standard_slots = [
        "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"
    ]

    # Fetch booked slots excluding cancelled
    existing_rdvs = RendezVous.objects.filter(
        medecin_id=medecin_id,
        date_rdv=target_date
    ).exclude(statut=RendezVous.StatutRendezVous.ANNULE)

    taken_times = set()
    for rdv in existing_rdvs:
        taken_times.add(rdv.heure.strftime("%H:%M"))

    now_time = datetime.datetime.now().time()
    creneaux_result = []

    for slot_str in standard_slots:
        slot_time = datetime.datetime.strptime(slot_str, "%H:%M").time()
        is_past = (target_date == today and slot_time <= now_time)
        is_booked = slot_str in taken_times

        disponible = not is_past and not is_booked
        raison = None
        if is_booked:
            raison = "Créneau déjà réservé"
        elif is_past:
            raison = "Heure passée"

        creneaux_result.append({
            "heure": slot_str,
            "disponible": disponible,
            "raison": raison
        })

    return Response({
        "medecin_id": medecin_id,
        "date": target_date.strftime("%Y-%m-%d"),
        "creneaux": creneaux_result
    }, status=status.HTTP_200_OK)


# Mes rendez-vous endpoint
@extend_schema(
    tags=["Rendez-vous"],
    summary="Lister mes rendez-vous",
    description="Retourne les rendez-vous du patient ou praticien connecté.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: RendezVousSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_mes_rendezvous(request):
    if request.user.is_authenticated:
        if getattr(request.user, "role", None) == "PATIENT" and hasattr(request.user, "patient"):
            rdvs = RendezVous.objects.filter(patient=request.user.patient).select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
            return paginate_response(rdvs, request, RendezVousSerializer)
        elif getattr(request.user, "role", None) == "MEDECIN" and hasattr(request.user, "medecin"):
            rdvs = RendezVous.objects.filter(medecin=request.user.medecin).select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
            return paginate_response(rdvs, request, RendezVousSerializer)
        elif getattr(request.user, "role", None) in ["ADMINISTRATEUR", "INFIRMIER"]:
            rdvs = RendezVous.objects.all().select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
            return paginate_response(rdvs, request, RendezVousSerializer)

    # Guest lookup by phone or email parameter
    phone = request.query_params.get("telephone") or request.query_params.get("phone")
    email = request.query_params.get("email")
    if phone or email:
        from django.db.models import Q
        q_filter = Q()
        if phone:
            q_filter |= Q(patient__id_utilisateur__telephone=phone)
        if email:
            q_filter |= Q(patient__id_utilisateur__email=email)
        rdvs = RendezVous.objects.filter(q_filter).select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
        return paginate_response(rdvs, request, RendezVousSerializer)

    # Return active sample rendezvous if guest
    rdvs = RendezVous.objects.all().select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")[:10]
    return paginate_response(rdvs, request, RendezVousSerializer)


@extend_schema(
    tags=["Rendez-vous"],
    summary="Créer un rendez-vous",
    description="Enregistre un nouveau rendez-vous entre un patient et un médecin.",
    request=RendezVousSerializer,
    responses={201: RendezVousSerializer, 400: ErrorResponseSerializer, 409: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def create_rendezvous(request):
    data = request.data.copy()

    # Enforce mandatory motif
    motif = data.get("motif")
    if not motif or not str(motif).strip():
        return Response({"motif": ["Le motif du rendez-vous est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

    # Auto-associate patient if authenticated patient
    if request.user.is_authenticated and hasattr(request.user, "patient") and not data.get("id_patient") and not data.get("patient_id"):
        data["id_patient"] = request.user.patient.id_patient
    elif not data.get("id_patient") and not data.get("patient_id"):
        # If guest, pick or attach patient record (e.g. first patient or demo patient)
        first_patient = Patient.objects.first()
        if first_patient:
            data["id_patient"] = first_patient.id_patient

    serializer = RendezVousSerializer(data=data)
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

