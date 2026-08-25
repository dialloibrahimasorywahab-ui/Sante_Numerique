from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer
from .patientSerializers import PatientSerializer
from .patientServices import PatientService


# Création du service
patient_service = PatientService()


# Enregistrement d'un patient
@extend_schema(
    tags=["Patients"],
    summary="Créer un patient",
    description="Enregistre un nouveau patient (et le compte utilisateur associé).",
    request=PatientSerializer,
    responses={201: PatientSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
def create_patient(request):
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
    responses={200: PatientSerializer(many=True)},
)
@api_view(["GET"])
def get_all_patient(request):
    patients = patient_service.get_all_patient()
    serializer = PatientSerializer(patients, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Recuperer et afficher un patient grace a son id
@extend_schema(
    tags=["Patients"],
    summary="Récupérer un patient",
    description="Retourne un patient à partir de son identifiant.",
    responses={200: PatientSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET"])
def get_patient(request, patient_id):
    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

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
def update_patient(request, patient_id):
    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = PatientSerializer(patient, data=request.data, partial=partial)

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
