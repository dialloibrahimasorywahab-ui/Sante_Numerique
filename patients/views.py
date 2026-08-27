from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .patientSerializers import PatientSerializer
from .patientServices import PatientService


# Création du service
patient_service = PatientService()


# Enregistrement et listing des patients
@extend_schema(
    tags=["Patients"],
    summary="Lister ou créer un patient",
    description="Retourne la liste des patients (GET avec ?search= optionnel) ou enregistre un nouveau patient (POST).",
    parameters=[SEARCH_PARAM, *PAGINATION_PARAMS],
    request=PatientSerializer,
    responses={200: PatientSerializer(many=True), 201: PatientSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsStaffOrAdmin])
def create_patient(request):
    if request.method == "GET":
        query = request.query_params.get("search") or request.query_params.get("q")
        if query:
            patients = patient_service.search_patients(query)
        else:
            patients = patient_service.get_all_patient()
        return paginate_response(patients, request, PatientSerializer)

    serializer = PatientSerializer(data=request.data)

    if serializer.is_valid():
        try:
            patient = patient_service.createPatient(**serializer.validated_data)
            serializer = PatientSerializer(patient)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un patient ou utilisateur avec cet identifiant, email, téléphone existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Recuperer tous les patients
@extend_schema(
    tags=["Patients"],
    summary="Lister les patients",
    description="Retourne la liste de tous les patients enregistrés.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: PatientSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsStaffOrAdmin])
def get_all_patient(request):
    patients = patient_service.get_all_patient()
    return paginate_response(patients, request, PatientSerializer)


# Recuperer, modifier ou supprimer un patient grace a son id
@extend_schema(
    tags=["Patients"],
    summary="Récupérer, modifier ou supprimer un patient",
    description="Retourne, modifie ou supprime un patient à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=PatientSerializer,
    responses={200: PatientSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_patient(request, patient_id):
    if request.method in ["PUT", "PATCH"]:
        return update_patient(request, patient_id)
    elif request.method == "DELETE":
        return delete_patient(request, patient_id)

    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, patient)

    serializer = PatientSerializer(patient)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Modifier les informations d'un patient
@extend_schema(
    tags=["Patients"],
    summary="Modifier un patient",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) les informations d'un patient.",
    request=PatientSerializer,
    responses={200: PatientSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_patient(request, patient_id):
    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    deny_unless_owner_or_staff(request, patient)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = PatientSerializer(patient, data=request.data, partial=partial, context={"request": request})

    if serializer.is_valid():
        try:
            patient = patient_service.update_patient(patient, **serializer.validated_data)
            serializer = PatientSerializer(patient)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un patient ou utilisateur avec cet identifiant, email, téléphone existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Désactiver (soft delete) ou supprimer un patient
@extend_schema(
    tags=["Patients"],
    summary="Supprimer / désactiver un patient",
    description="Désactive (soft delete) le dossier patient, ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_patient(request, patient_id):
    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    patient_service.delete_patient(patient, hard=hard)

    if hard:
        return Response(
            {"message": "Dossier patient supprimé définitivement avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Compte patient désactivé (archivé) avec succès. L'historique médical a été préservé."},
        status=status.HTTP_200_OK
    )
