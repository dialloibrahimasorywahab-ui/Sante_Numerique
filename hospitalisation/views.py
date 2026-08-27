from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    SEARCH_PARAM,
)
from .hospitalisationSerializers import HospitalisationReadSerializer, HospitalisationSerializer
from .hospitalisationServices import HospitalisationService

hospitalisation_service = HospitalisationService()


@extend_schema(
    tags=["Hospitalisation"],
    summary="Lister ou créer une hospitalisation",
    description="GET: Liste l'ensemble des hospitalisations avec filtres (patient, médecin, lit, statut, recherche, all).\nPOST: Admet un nouveau patient en hospitalisation.",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant patient."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant médecin."),
        OpenApiParameter(name="lit_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant du lit."),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Filtrer par statut (PROGRAMMEE, EN_COURS, TERMINEE, ANNULEE)."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les hospitalisations inactives/archivées si true."),
        SEARCH_PARAM,
    ],
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer(many=True),
        201: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def hospitalisation_list_create_view(request):
    if request.method == "GET":
        if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
            return Response({"error": "Accès réservé au personnel soignant et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = hospitalisation_service.repository.get_all_hospitalisations(actif_only=actif_only)

        patient_id = request.query_params.get("patient_id") or request.query_params.get("id_patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        medecin_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
        if medecin_id:
            qs = qs.filter(medecin_id=medecin_id)

        lit_id = request.query_params.get("lit_id") or request.query_params.get("id_lit")
        if lit_id:
            qs = qs.filter(lit_id=lit_id)

        statut_param = request.query_params.get("statut")
        if statut_param:
            qs = qs.filter(statut=statut_param)

        search_query = request.query_params.get("search")
        if search_query:
            qs = qs.filter(
                patient__idUtilisateur__nom__icontains=search_query
            ) | qs.filter(
                patient__idUtilisateur__prenom__icontains=search_query
            ) | qs.filter(
                motif__icontains=search_query
            )

        serializer = HospitalisationReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Seul un médecin ou administrateur peut prescrire une hospitalisation."}, status=status.HTTP_403_FORBIDDEN)

        serializer = HospitalisationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                hospitalisation = hospitalisation_service.admettre_patient(**serializer.validated_data)
                read_serializer = HospitalisationReadSerializer(hospitalisation)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Hospitalisation"],
    summary="Détail, mise à jour partielle ou totale d'une hospitalisation",
    description="Accède aux détails d'une hospitalisation ou met à jour ses informations.",
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def hospitalisation_detail_view(request, pk):
    hospitalisation = hospitalisation_service.repository.get_hospitalisation_by_id(pk)
    if not hospitalisation:
        return Response({"error": f"Hospitalisation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, hospitalisation)

    if request.method == "GET":
        serializer = HospitalisationReadSerializer(hospitalisation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
        return Response({"error": "Action réservée au personnel soignant et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

    partial = (request.method == "PATCH")
    serializer = HospitalisationSerializer(hospitalisation, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = hospitalisation_service.mettre_a_jour_hospitalisation(pk, **serializer.validated_data)
            return Response(HospitalisationReadSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Hospitalisation"],
    summary="Clôturer une hospitalisation (Sortie du patient)",
    description="Marque l'hospitalisation comme TERMINEE, enregistre la date de sortie et libère le lit.",
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsStaffOrAdmin])
def hospitalisation_cloturer_view(request, pk):
    observation = request.data.get("observation")
    try:
        hospitalisation = hospitalisation_service.cloturer_hospitalisation(pk, observation_finale=observation)
        if not hospitalisation:
            return Response({"error": f"Hospitalisation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalisationReadSerializer(hospitalisation).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Hospitalisation"],
    summary="Supprimer ou archiver une hospitalisation",
    description="Par défaut désactive l'hospitalisation (actif=False, statut=ANNULEE). Si hard=true, la supprime définitivement de la base.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsMedecinOuAdmin])
def hospitalisation_delete_view(request, pk):
    hard = request.query_params.get("hard", "false").lower() == "true"
    success = hospitalisation_service.supprimer_hospitalisation(pk, hard=hard)
    if not success:
        return Response({"error": f"Hospitalisation #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Hospitalisation #{pk} supprimée définitivement." if hard else f"Hospitalisation #{pk} archivée (annulée)."
    return Response({"message": msg}, status=status.HTTP_200_OK)
