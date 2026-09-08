from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsAdmin, IsMedecinOuAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .models import Medecin, DisponibiliteMedecin, IndisponibiliteMedecin
from .medecinSerializers import (
    MedecinSerializer,
    DisponibiliteMedecinSerializer,
    IndisponibiliteMedecinSerializer,
)
from .medecinServices import MedecinService


medecin_service = MedecinService()


# Enregistrement et listing des médecins
@extend_schema(
    tags=["Médecins"],
    summary="Lister ou créer un médecin",
    description="Retourne la liste des médecins (GET avec filtres ?service=, ?specialite=, ?search=, ?all=) ou enregistre un nouveau médecin (POST).",
    parameters=[
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                          description="Inclure aussi les médecins inactifs si true."),
        OpenApiParameter(name="service", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par service ou spécialité (alias : specialite)."),
        OpenApiParameter(name="specialite", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par spécialité."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=MedecinSerializer,
    responses={200: MedecinSerializer(many=True), 201: MedecinSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def create_medecin(request):
    if request.method == "GET":
        actif_only = request.query_params.get("all", "false").lower() != "true"
        specialite = request.query_params.get("service") or request.query_params.get("specialite")
        search_q = request.query_params.get("search") or request.query_params.get("q")
        if specialite:
            medecins = medecin_service.get_medecins_by_specialite(specialite, actif_only=actif_only)
        elif search_q:
            medecins = medecin_service.search_medecins(search_q, actif_only=actif_only)
        else:
            medecins = medecin_service.get_all_medecin(actif_only=actif_only)
        return paginate_response(medecins, request, MedecinSerializer)

    if not request.user.is_authenticated or getattr(request.user, "role", None) != "ADMINISTRATEUR":
        return Response({"message": "Seul un administrateur peut enregistrer un médecin."}, status=status.HTTP_403_FORBIDDEN)

    serializer = MedecinSerializer(data=request.data)

    if serializer.is_valid():
        try:
            medecin = medecin_service.createMedecin(**serializer.validated_data)
            serializer = MedecinSerializer(medecin)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Impossible d'enregistrer ce médecin.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer tous les médecins (avec support du filtre ?service=... ou ?specialite=...)
@extend_schema(
    tags=["Médecins"],
    summary="Lister les médecins",
    description="Retourne la liste de tous les médecins avec filtres optionnels ?all=, ?service=, ?specialite=.",
    parameters=[
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                          description="Inclure aussi les médecins inactifs si true."),
        OpenApiParameter(name="service", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par service ou spécialité (alias : specialite)."),
        OpenApiParameter(name="specialite", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                          description="Filtre par spécialité."),
        *PAGINATION_PARAMS,
    ],
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_medecin(request):
    actif_only = request.query_params.get("all", "false").lower() != "true"
    specialite = request.query_params.get("service") or request.query_params.get("specialite")
    if specialite:
        medecins = medecin_service.get_medecins_by_specialite(specialite, actif_only=actif_only)
    else:
        medecins = medecin_service.get_all_medecin(actif_only=actif_only)

    return paginate_response(medecins, request, MedecinSerializer)


# Récupérer les médecins d'un service / spécialité
@extend_schema(
    tags=["Médecins"],
    summary="Lister les médecins d'une spécialité",
    description="Retourne les médecins rattachés à la spécialité/service donné(e).",
    parameters=[*PAGINATION_PARAMS],
    responses={200: MedecinSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_medecins_by_specialite(request, specialite):
    medecins = medecin_service.get_medecins_by_specialite(specialite)
    return paginate_response(medecins, request, MedecinSerializer)


# Récupérer, modifier ou supprimer un médecin grâce à son ID
@extend_schema(
    tags=["Médecins"],
    summary="Récupérer, modifier ou supprimer un médecin",
    description="Retourne, modifie ou supprime un médecin par son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=MedecinSerializer,
    responses={200: MedecinSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def get_medecin(request, medecin_id):
    if request.method in ["PUT", "PATCH"]:
        deny = deny_unless_owner_or_staff(request, medecin_id, id_field="id_medecin")
        if deny:
            return deny
        return update_medecin(request, medecin_id)
    elif request.method == "DELETE":
        if not request.user.is_authenticated or getattr(request.user, "role", None) != "ADMINISTRATEUR":
            return Response({"message": "Accès non autorisé."}, status=status.HTTP_403_FORBIDDEN)
        return delete_medecin(request, medecin_id)

    medecin = medecin_service.get_medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = MedecinSerializer(medecin)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Modifier les informations d'un médecin
@extend_schema(
    tags=["Médecins"],
    summary="Modifier un médecin",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un médecin.",
    request=MedecinSerializer,
    responses={200: MedecinSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, medecin)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MedecinSerializer(medecin, data=request.data, partial=partial, context={"request": request})

    if serializer.is_valid():
        try:
            medecin = medecin_service.update_medecin(medecin, **serializer.validated_data)
            serializer = MedecinSerializer(medecin)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un médecin ou utilisateur avec cet identifiant, email, téléphone ou numéro d'ordre existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Désactiver (soft delete) ou supprimer un médecin
@extend_schema(
    tags=["Médecins"],
    summary="Supprimer / désactiver un médecin",
    description="Désactive (soft delete) la fiche médecin, ou la supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    medecin_service.delete_medecin(medecin, hard=hard)

    if hard:
        return Response(
            {"message": "Fiche médecin supprimée définitivement avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Compte médecin désactivé (archivé) avec succès."},
        status=status.HTTP_200_OK
    )


# ==========================================
# GESTION DES DISPONIBILITÉS & CRÉNEAUX
# ==========================================

def _get_target_medecin(request):
    """Helper pour récupérer le profil médecin associé à la requête."""
    user_role = getattr(request.user, "role", None)
    if user_role == "MEDECIN":
        return getattr(request.user, "medecin", None)
    elif user_role == "ADMINISTRATEUR":
        medecin_id = request.query_params.get("medecin_id") or request.data.get("medecin")
        if medecin_id:
            try:
                return Medecin.objects.filter(id_medecin=int(medecin_id)).first()
            except (ValueError, TypeError):
                return None
    return None


@extend_schema(
    tags=["Médecins"],
    summary="Lister ou configurer les disponibilités",
    description="GET: Retourne les créneaux réguliers de la semaine pour le médecin connecté ou par ?medecin_id=.\nPOST: Crée ou met à jour la disponibilité pour un jour de la semaine.",
    request=DisponibiliteMedecinSerializer,
    responses={200: DisponibiliteMedecinSerializer(many=True), 201: DisponibiliteMedecinSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def disponibilites_list_create_view(request):
    medecin = _get_target_medecin(request)
    if not medecin:
        # En GET, permettre la consultation publique par paramètre medecin_id
        m_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
        if m_id:
            try:
                medecin = Medecin.objects.filter(id_medecin=int(m_id)).first()
            except (ValueError, TypeError):
                pass
        if not medecin:
            return Response(
                {"error": "Médecin introuvable ou profil praticien non associé à ce compte."},
                status=status.HTTP_404_NOT_FOUND
            )

    if request.method == "GET":
        dispos = DisponibiliteMedecin.objects.filter(medecin=medecin).order_by("jour_semaine")
        serializer = DisponibiliteMedecinSerializer(dispos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Action réservée aux médecins."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data["medecin"] = medecin.idMedecin
        jour = data.get("jour_semaine") or data.get("jourSemaine")
        if jour is None:
            return Response({"error": "Le champ jour_semaine est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Si une règle existe déjà pour ce jour, la mettre à jour, sinon créer
        existing = DisponibiliteMedecin.objects.filter(medecin=medecin, jour_semaine=jour).first()
        serializer = DisponibiliteMedecinSerializer(existing, data=data, partial=bool(existing))
        if serializer.is_valid():
            dispo = serializer.save(medecin=medecin)
            return Response(
                DisponibiliteMedecinSerializer(dispo).data,
                status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Médecins"],
    summary="Mettre à jour l'ensemble de la semaine en une seule requête",
    description="Reçoit une liste d'objets jourSemaine / horaires et configure tout le planning hebdomadaire.",
    request=DisponibiliteMedecinSerializer(many=True),
    responses={200: DisponibiliteMedecinSerializer(many=True), 400: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsMedecinOuAdmin])
def disponibilites_bulk_view(request):
    medecin = _get_target_medecin(request)
    if not medecin:
        return Response({"error": "Profil praticien non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    days_data = request.data if isinstance(request.data, list) else request.data.get("disponibilites", [])
    if not isinstance(days_data, list):
        return Response({"error": "Format invalide. Une liste d'objets est attendue."}, status=status.HTTP_400_BAD_REQUEST)

    saved_items = []
    from django.db import transaction
    with transaction.atomic():
        for item in days_data:
            if not isinstance(item, dict):
                continue
            jour = item.get("jour_semaine") if "jour_semaine" in item else item.get("jourSemaine")
            if jour is None:
                continue
            item_data = item.copy()
            item_data["medecin"] = medecin.idMedecin
            existing = DisponibiliteMedecin.objects.filter(medecin=medecin, jour_semaine=jour).first()
            serializer = DisponibiliteMedecinSerializer(existing, data=item_data, partial=bool(existing))
            if serializer.is_valid():
                obj = serializer.save(medecin=medecin)
                saved_items.append(obj)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    all_dispos = DisponibiliteMedecin.objects.filter(medecin=medecin).order_by("jour_semaine")
    return Response(DisponibiliteMedecinSerializer(all_dispos, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Médecins"],
    summary="Modifier ou supprimer une disponibilité",
    responses={200: DisponibiliteMedecinSerializer, 204: None, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsMedecinOuAdmin])
def disponibilite_detail_view(request, pk):
    medecin = _get_target_medecin(request)
    dispo = DisponibiliteMedecin.objects.filter(pk=pk).first()
    if not dispo:
        return Response({"message": "Créneau de disponibilité introuvable"}, status=status.HTTP_404_NOT_FOUND)

    if getattr(request.user, "role", None) != "ADMINISTRATEUR" and dispo.medecin != medecin:
        return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(DisponibiliteMedecinSerializer(dispo).data, status=status.HTTP_200_OK)

    elif request.method in ["PUT", "PATCH"]:
        serializer = DisponibiliteMedecinSerializer(dispo, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        dispo.delete()
        return Response({"message": "Créneau supprimé avec succès."}, status=status.HTTP_200_OK)


# ==========================================
# GESTION DES INDISPONIBILITÉS & CONGÉS
# ==========================================

@extend_schema(
    tags=["Médecins"],
    summary="Lister ou enregistrer une indisponibilité",
    description="GET: Retourne les indisponibilités / congés du médecin connecté.\nPOST: Enregistre une absence ponctuelle ou une période de congés.",
    request=IndisponibiliteMedecinSerializer,
    responses={200: IndisponibiliteMedecinSerializer(many=True), 201: IndisponibiliteMedecinSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def indisponibilites_list_create_view(request):
    medecin = _get_target_medecin(request)
    if not medecin:
        m_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
        if m_id:
            try:
                medecin = Medecin.objects.filter(id_medecin=int(m_id)).first()
            except (ValueError, TypeError):
                pass
        if not medecin:
            return Response(
                {"error": "Médecin introuvable ou profil praticien non associé."},
                status=status.HTTP_404_NOT_FOUND
            )

    if request.method == "GET":
        indispos = IndisponibiliteMedecin.objects.filter(medecin=medecin, actif=True).order_by("-date_debut")
        serializer = IndisponibiliteMedecinSerializer(indispos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Action réservée aux médecins."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data["medecin"] = medecin.idMedecin
        serializer = IndisponibiliteMedecinSerializer(data=data)
        if serializer.is_valid():
            indispo = serializer.save(medecin=medecin)
            return Response(IndisponibiliteMedecinSerializer(indispo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Médecins"],
    summary="Modifier ou supprimer une indisponibilité",
    responses={200: IndisponibiliteMedecinSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsMedecinOuAdmin])
def indisponibilite_detail_view(request, pk):
    medecin = _get_target_medecin(request)
    indispo = IndisponibiliteMedecin.objects.filter(pk=pk).first()
    if not indispo:
        return Response({"message": "Indisponibilité introuvable"}, status=status.HTTP_404_NOT_FOUND)

    if getattr(request.user, "role", None) != "ADMINISTRATEUR" and indispo.medecin != medecin:
        return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(IndisponibiliteMedecinSerializer(indispo).data, status=status.HTTP_200_OK)

    elif request.method in ["PUT", "PATCH"]:
        serializer = IndisponibiliteMedecinSerializer(indispo, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        indispo.delete()
        return Response({"message": "Indisponibilité supprimée avec succès."}, status=status.HTTP_200_OK)

