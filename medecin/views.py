from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .medecinSerializers import MedecinSerializer
from .medecinServices import MedecinService


medecin_service = MedecinService()


# Enregistrement d'un médecin
@api_view(["POST"])
def create_medecin(request):
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
                {"error": "Un médecin ou utilisateur avec cet identifiant, email, téléphone ou numéro d'ordre existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer tous les médecins (avec support du filtre ?service=... ou ?specialite=...)
@api_view(["GET"])
def get_all_medecin(request):
    specialite = request.query_params.get("service") or request.query_params.get("specialite")
    if specialite:
        medecins = medecin_service.get_medecins_by_specialite(specialite)
    else:
        medecins = medecin_service.get_all_medecin()

    serializer = MedecinSerializer(medecins, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer les médecins d'un service / spécialité
@api_view(["GET"])
def get_medecins_by_specialite(request, specialite):
    medecins = medecin_service.get_medecins_by_specialite(specialite)
    serializer = MedecinSerializer(medecins, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer et afficher un médecin grâce à son ID
@api_view(["GET"])
def get_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

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
@api_view(["PUT", "PATCH"])
def update_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MedecinSerializer(medecin, data=request.data, partial=partial)

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


# Supprimer un médecin
@api_view(["DELETE"])
def delete_medecin(request, medecin_id):
    medecin = medecin_service.get_Medecin(medecin_id)

    if medecin is None:
        return Response(
            {"message": "Médecin introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    medecin_service.delete_medecin(medecin)

    return Response(
        {"message": "Médecin supprimé avec succès"},
        status=status.HTTP_204_NO_CONTENT
    )
