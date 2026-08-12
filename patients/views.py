from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .patientSerializers import PatientSerializer
from .patientServices import PatientService


# Création du service
patient_service = PatientService()


#Enregistrement d'un patient
@api_view(["POST"])
def create_patient(request):

    serializer = PatientSerializer(data=request.data)

    if serializer.is_valid():

        patient = patient_service.createPatient(
            **serializer.validated_data
        )

        serializer = PatientSerializer(patient)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# recuperer tous les patients 
@api_view(["GET"])
def get_all_patient(request):

    patients = patient_service.get_all_patient()

    serializer = PatientSerializer(
        patients,
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# recuperer et afficher un patient grace à son id
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
@api_view(["PUT"])
def update_patient(request, patient_id):

    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PatientSerializer(
        patient,
        data=request.data
    )

    if serializer.is_valid():

        patient = patient_service.update_patient(
            patient,
            **serializer.validated_data
        )

        serializer = PatientSerializer(patient)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================
# SUPPRIMER UN PATIENT
# =========================
@api_view(["DELETE"])
def delete_patient(request, patient_id):

    patient = patient_service.get_Patient(patient_id)

    if patient is None:
        return Response(
            {"message": "Patient introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    patient_service.delete_patient(patient)

    return Response(
        {"message": "Patient supprimé avec succès"},
        status=status.HTTP_204_NO_CONTENT
    )

