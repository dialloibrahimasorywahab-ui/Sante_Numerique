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
from medecin.models import Medecin, DisponibiliteMedecin, IndisponibiliteMedecin
import datetime

rendezvous_service = RendezVousService()


def _rendezvous_action_response(message_example):
    return inline_serializer(
        name=f"RendezVousActionResponse_{message_example}",
        fields={
            "message": serializers.CharField(default=f"Rendez-vous {message_example} avec succès."),
            "rendezvous": RendezVousSerializer(),
        }
    )


# Créneaux disponibles pour un médecin à une date donnée
@extend_schema(
    tags=["Rendez-vous"],
    summary="Obtenir les créneaux disponibles pour un médecin",
    description="Retourne les créneaux horaires d'une journée en tenant compte des disponibilités hebdomadaires, des indisponibilités/congés du praticien et des rendez-vous déjà réservés.",
    parameters=[
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=True,
                          description="Identifiant du médecin."),
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=False,
                          description="Date souhaitée (format YYYY-MM-DD). Défaut : aujourd'hui."),
    ],
    responses={200: inline_serializer(
        name="CreneauxResponse",
        fields={
            "medecin_id": serializers.IntegerField(),
            "date": serializers.CharField(),
            "jour_semaine": serializers.IntegerField(),
            "est_indisponible": serializers.BooleanField(),
            "motif_indisponibilite": serializers.CharField(allow_null=True),
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

    # 1. Vérification des indisponibilités (congés, formations, absences)
    active_indispos = IndisponibiliteMedecin.objects.filter(
        medecin_id=medecin_id,
        actif=True,
        date_debut__lte=target_date,
        date_fin__gte=target_date
    )
    all_day_indispo = active_indispos.filter(toute_la_journee=True).first()

    # 2. Détermination des créneaux de travail du médecin pour ce jour de la semaine
    weekday = target_date.weekday()  # 0=Lundi, ..., 6=Dimanche
    has_custom_schedule = DisponibiliteMedecin.objects.filter(medecin_id=medecin_id).exists()

    generated_slots = []
    if has_custom_schedule:
        day_dispo = DisponibiliteMedecin.objects.filter(
            medecin_id=medecin_id,
            jour_semaine=weekday,
            actif=True
        ).first()

        if day_dispo:
            # Génération par pas de durée_créneau
            duree = datetime.timedelta(minutes=max(15, day_dispo.duree_creneau or 45))
            cur_time = datetime.datetime.combine(target_date, day_dispo.heure_debut)
            end_time = datetime.datetime.combine(target_date, day_dispo.heure_fin)
            pause_deb = datetime.datetime.combine(target_date, day_dispo.pause_debut) if day_dispo.pause_debut else None
            pause_fin = datetime.datetime.combine(target_date, day_dispo.pause_fin) if day_dispo.pause_fin else None

            while cur_time + duree <= end_time:
                slot_time = cur_time.time()
                # Sauter la pause déjeuner
                in_pause = False
                if pause_deb and pause_fin:
                    if pause_deb <= cur_time < pause_fin:
                        in_pause = True
                if not in_pause:
                    generated_slots.append(slot_time.strftime("%H:%M"))
                cur_time += duree
        else:
            # Médecin ne consulte pas ce jour
            generated_slots = []
    else:
        # Fallback standard si aucun créneau personnalisé n'a encore été configuré
        generated_slots = [
            "08:30", "09:15", "10:00", "10:45", "11:30",
            "14:00", "14:45", "15:30", "16:15"
        ]

    # 3. Récupérer les rendez-vous existants déjà pris
    existing_rdvs = RendezVous.objects.filter(
        medecin_id=medecin_id,
        date_rdv=target_date
    ).exclude(statut=RendezVous.StatutRendezVous.ANNULE)

    taken_times = {rdv.heure.strftime("%H:%M") for rdv in existing_rdvs}
    now_time = datetime.datetime.now().time()
    creneaux_result = []

    for slot_str in generated_slots:
        slot_time = datetime.datetime.strptime(slot_str, "%H:%M").time()
        is_past = (target_date == today and slot_time <= now_time)
        is_booked = slot_str in taken_times

        # Vérifier si ce créneau tombe dans une indisponibilité
        is_indispo = False
        indispo_motif = None
        if all_day_indispo:
            is_indispo = True
            indispo_motif = all_day_indispo.motif or "Médecin absent / indisponible"
        else:
            for ind in active_indispos.filter(toute_la_journee=False):
                if ind.heure_debut and ind.heure_fin:
                    if ind.heure_debut <= slot_time < ind.heure_fin:
                        is_indispo = True
                        indispo_motif = ind.motif or "Médecin indisponible sur ce créneau"
                        break

        disponible = not is_past and not is_booked and not is_indispo
        raison = None
        if is_indispo:
            raison = indispo_motif or "Médecin indisponible"
        elif is_booked:
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
        "jour_semaine": weekday,
        "est_indisponible": bool(all_day_indispo),
        "motif_indisponibilite": all_day_indispo.motif if all_day_indispo else None,
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
            patient_id = request.query_params.get("patient_id") or request.query_params.get("id_patient")
            if patient_id:
                try:
                    pid = int(patient_id)
                    rdvs = RendezVous.objects.filter(patient_id=pid).select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
                    return paginate_response(rdvs, request, RendezVousSerializer)
                except (ValueError, TypeError):
                    pass
            rdvs = RendezVous.objects.all().select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
            return paginate_response(rdvs, request, RendezVousSerializer)

    # Guest lookup by patient_id, phone or email parameter
    patient_id = request.query_params.get("patient_id") or request.query_params.get("id_patient")
    phone = request.query_params.get("telephone") or request.query_params.get("phone")
    email = request.query_params.get("email")
    if patient_id or phone or email:
        from django.db.models import Q
        q_filter = Q()
        if patient_id:
            try:
                pid = int(patient_id)
                q_filter |= Q(patient_id=pid) | Q(patient__id_utilisateur_id=pid)
            except (ValueError, TypeError):
                pass
        if phone:
            q_filter |= Q(patient__id_utilisateur__telephone=phone)
        if email:
            q_filter |= Q(patient__id_utilisateur__email=email)
        rdvs = RendezVous.objects.filter(q_filter).select_related("patient", "medecin", "patient__id_utilisateur", "medecin__id_utilisateur").order_by("-date_rdv", "-heure")
        return paginate_response(rdvs, request, RendezVousSerializer)

    # Retourner une liste vide si aucun patient n'est identifié (ne pas exposer les données des autres patients)
    return Response({
        "count": 0,
        "total_pages": 1,
        "current_page": 1,
        "page_size": 20,
        "next": None,
        "previous": None,
        "results": []
    }, status=status.HTTP_200_OK)


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

    # Enforce mandatory motif or reason
    motif = data.get("motif") or data.get("reason")
    if not motif or not str(motif).strip():
        return Response({"motif": ["Le motif du rendez-vous est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

    # Auto-associate patient if authenticated patient and prevent spoofing
    if request.user.is_authenticated:
        if getattr(request.user, "role", None) == "PATIENT" or hasattr(request.user, "patient"):
            if hasattr(request.user, "patient"):
                patient_rec = request.user.patient
            else:
                from django.utils import timezone
                patient_rec, _ = Patient.objects.get_or_create(
                    id_utilisateur=request.user,
                    defaults={
                        "sexe": "M",
                        "adresse": "Conakry",
                        "groupe_sanguin": "O+",
                        "personne_a_contacter": request.user.telephone or "Non renseigné",
                        "date_inscription": timezone.now().date(),
                    }
                )
            data["id_patient"] = patient_rec.id_patient
            data.pop("patient_id", None)
            data.pop("patient", None)

    # Si id_patient, patient_id ou patient est fourni (pour admin ou personnel médical)
    pid = data.get("id_patient") or data.get("patient_id") or data.get("patient")
    if pid:
        try:
            pid_int = int(pid)
            if not Patient.objects.filter(id_patient=pid_int).exists():
                user_match = User.objects.filter(id_user=pid_int).first()
                if user_match:
                    if hasattr(user_match, "patient"):
                        data["id_patient"] = user_match.patient.id_patient
                    else:
                        from django.utils import timezone
                        p, _ = Patient.objects.get_or_create(
                            id_utilisateur=user_match,
                            defaults={
                                "sexe": "M",
                                "adresse": "Conakry",
                                "groupe_sanguin": "O+",
                                "personne_a_contacter": user_match.telephone or "Non renseigné",
                                "date_inscription": timezone.now().date(),
                            }
                        )
                        data["id_patient"] = p.id_patient
        except (ValueError, TypeError):
            pass

    if not data.get("id_patient") and not data.get("patient_id"):
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

