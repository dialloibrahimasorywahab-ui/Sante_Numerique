from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    PAGINATION_PARAMS,
    SEARCH_PARAM,
)
from .ligneSerializers import LigneOrdonnanceSerializer
from .ligneServices import LigneOrdonnanceService

ligne_service = LigneOrdonnanceService()


@extend_schema(
    tags=["LigneOrdonnance"],
    summary="Lister ou ajouter une ligne de prescription",
    description="GET: Liste les lignes de prescription avec filtres optionnels (?ordonnance_id=, ?search=, ?all=).\nPOST: Ajoute une nouvelle ligne de prescription à une ordonnance.",
    parameters=[
        OpenApiParameter(name="ordonnance_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant d'ordonnance."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure les lignes inactives si true."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=LigneOrdonnanceSerializer,
    responses={
        200: LigneOrdonnanceSerializer(many=True),
        201: LigneOrdonnanceSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def ligne_ordonnance_list_create_view(request):
    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        if user_role == "INFIRMIER":
            return Response(
                {"error": "Accès refusé. Les infirmiers doivent consulter une ordonnance spécifique."},
                status=status.HTTP_403_FORBIDDEN
            )

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = ligne_service.get_all_lignes(actif_only=actif_only)

        # Filtrage selon le rôle
        if user_role == "ADMINISTRATEUR":
            pass
        elif user_role == "MEDECIN":
            qs = qs.filter(ordonnance__consultation__medecin__id_utilisateur=request.user)
        elif user_role == "PATIENT":
            qs = qs.filter(ordonnance__consultation__patient__id_utilisateur=request.user)
        else:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        # Filtre par ordonnance
        ordonnance_id = request.query_params.get("ordonnance_id") or request.query_params.get("id_ordonnance")
        if ordonnance_id:
            qs = qs.filter(ordonnance_id=ordonnance_id)

        # Recherche textuelle
        search = request.query_params.get("search") or request.query_params.get("q")
        if search:
            qs = qs.filter(medicament__icontains=search) | qs.filter(posologie__icontains=search) | qs.filter(forme__icontains=search)

        return paginate_response(qs, request, LigneOrdonnanceSerializer)

    elif request.method == "POST":
        if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response(
                {"error": "Seul un médecin ou un administrateur peut prescrire une ligne d'ordonnance."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LigneOrdonnanceSerializer(data=request.data)
        if serializer.is_valid():
            ordonnance = serializer.validated_data.get("ordonnance")
            if not ordonnance:
                return Response({"error": "L'ordonnance parente est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

            if user_role == "MEDECIN":
                consultation = getattr(ordonnance, 'consultation', None)
                if not consultation or not consultation.medecin or consultation.medecin.id_utilisateur != request.user:
                    return Response(
                        {"error": "Accès refusé. Vous ne pouvez modifier que les prescriptions de vos propres consultations."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            ligne = ligne_service.create_ligne(**serializer.validated_data)
            return Response(LigneOrdonnanceSerializer(ligne).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["LigneOrdonnance"],
    summary="Détail, modification ou suppression d'une ligne de prescription",
    description="GET: Détail de la ligne.\nPUT/PATCH: Mise à jour de la posologie ou du dosage.\nDELETE: Suppression logique ou physique (?hard=true).",
    parameters=[HARD_DELETE_PARAM],
    request=LigneOrdonnanceSerializer,
    responses={
        200: LigneOrdonnanceSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def ligne_ordonnance_detail_view(request, pk: int):
    ligne = ligne_service.get_ligne(pk)
    if not ligne:
        return Response({"error": "Ligne d'ordonnance introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, ligne.ordonnance)
    user_role = getattr(request.user, "role", None)

    if request.method == "GET":
        return Response(LigneOrdonnanceSerializer(ligne).data)

    # Modifications et suppressions réservées au médecin traitant ou admin
    if user_role not in ["MEDECIN", "ADMINISTRATEUR"]:
        return Response({"error": "Action réservée aux médecins ou administrateurs."}, status=status.HTTP_403_FORBIDDEN)

    if user_role == "MEDECIN":
        consultation = getattr(ligne.ordonnance, 'consultation', None)
        if not consultation or not consultation.medecin or consultation.medecin.id_utilisateur != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez modifier que les prescriptions de vos propres consultations."},
                status=status.HTTP_403_FORBIDDEN
            )

    if request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        serializer = LigneOrdonnanceSerializer(ligne, data=request.data, partial=partial)
        if serializer.is_valid():
            updated_ligne = ligne_service.update_ligne(ligne, **serializer.validated_data)
            return Response(LigneOrdonnanceSerializer(updated_ligne).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        hard = request.query_params.get("hard", "false").lower() == "true"
        ligne_service.delete_ligne(ligne, hard=hard)
        msg = "Ligne d'ordonnance définitivement supprimée." if hard else "Ligne d'ordonnance désactivée avec succès."
        return Response({"message": msg}, status=status.HTTP_200_OK)
