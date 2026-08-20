# pyrefly: ignore [missing-import]
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .rendezvousSerializers import RendezVousSerializer
from .rendezvousServices import RendezVousService

rendezvous_service = RendezVousService()


@api_view(["POST"])
def create_rendezvous(request):
    serializer = RendezVousSerializer(data=request.data)
    if serializer.is_valid():
        try:
            rdv = rendezvous_service.create_rendezvous(**serializer.validated_data)
            return Response(RendezVousSerializer(rdv).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Erreur lors de la création du rendez-vous.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
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

    serializer = RendezVousSerializer(rdvs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rendezvous_by_statut(request, statut):
    rdvs = rendezvous_service.get_rendezvous_by_statut(statut)
    serializer = RendezVousSerializer(rdvs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rendezvous_by_patient(request, patient_id):
    rdvs = rendezvous_service.get_rendezvous_by_patient(patient_id)
    serializer = RendezVousSerializer(rdvs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rendezvous_by_medecin(request, medecin_id):
    rdvs = rendezvous_service.get_rendezvous_by_medecin(medecin_id)
    serializer = RendezVousSerializer(rdvs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(RendezVousSerializer(rdv).data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def update_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = RendezVousSerializer(rdv, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = rendezvous_service.update_rendezvous(rdv, **serializer.validated_data)
            return Response(RendezVousSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Erreur lors de la modification.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "POST"])
def confirmer_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    updated = rendezvous_service.update_rendezvous(rdv, statut="CONFIRME")
    return Response(
        {"message": "Rendez-vous confirmé avec succès.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@api_view(["PATCH", "POST"])
def annuler_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    updated = rendezvous_service.update_rendezvous(rdv, statut="ANNULE")
    return Response(
        {"message": "Rendez-vous annulé.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@api_view(["PATCH", "POST"])
def terminer_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    updated = rendezvous_service.update_rendezvous(rdv, statut="TERMINE")
    return Response(
        {"message": "Rendez-vous marqué comme terminé.", "rendezvous": RendezVousSerializer(updated).data},
        status=status.HTTP_200_OK
    )


@api_view(["DELETE"])
def delete_rendezvous(request, rdv_id):
    rdv = rendezvous_service.get_rendezvous(rdv_id)
    if rdv is None:
        return Response({"message": "Rendez-vous introuvable"}, status=status.HTTP_404_NOT_FOUND)

    rendezvous_service.delete_rendezvous(rdv)
    return Response({"message": "Rendez-vous supprimé avec succès"}, status=status.HTTP_200_OK)

