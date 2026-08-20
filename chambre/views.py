from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .chambreSerializers import ChambreSerializer
from .chambreServices import ChambreService

chambre_service = ChambreService()


@api_view(["POST"])
def create_chambre(request):
    serializer = ChambreSerializer(data=request.data)
    if serializer.is_valid():
        try:
            chambre = chambre_service.create_chambre(**serializer.validated_data)
            if chambre.batiment:
                chambre.batiment.sync_nombre_chambres()
            return Response(ChambreSerializer(chambre).data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"error": "Une chambre avec ce numéro existe déjà dans ce bâtiment.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_chambres(request):
    batiment_id = request.query_params.get('batiment_id') or request.query_params.get('id_batiment')
    type_chambre = request.query_params.get('type_chambre') or request.query_params.get('type')
    statut = request.query_params.get('statut')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if batiment_id:
        chambres = chambre_service.get_chambres_by_batiment(batiment_id)
    elif type_chambre:
        chambres = chambre_service.get_chambres_by_type(type_chambre)
    elif statut:
        chambres = chambre_service.get_chambres_by_statut(statut)
    elif search_q:
        chambres = chambre_service.search_chambres(search_q)
    else:
        chambres = chambre_service.get_all_chambres()

    serializer = ChambreSerializer(chambres, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_chambres_by_type(request, type_chambre):
    chambres = chambre_service.get_chambres_by_type(type_chambre)
    serializer = ChambreSerializer(chambres, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_chambres_by_statut(request, statut):
    chambres = chambre_service.get_chambres_by_statut(statut)
    serializer = ChambreSerializer(chambres, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(["GET"])
def get_chambre(request, chambre_id):
    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(ChambreSerializer(chambre).data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def update_chambre(request, chambre_id):
    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = ChambreSerializer(chambre, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = chambre_service.update_chambre(chambre, **serializer.validated_data)
            if updated.batiment:
                updated.batiment.sync_nombre_chambres()
            return Response(ChambreSerializer(updated).data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": "Erreur d'intégrité.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_chambre(request, chambre_id):
    chambre = chambre_service.get_chambre(chambre_id)
    if chambre is None:
        return Response({"message": "Chambre introuvable"}, status=status.HTTP_404_NOT_FOUND)

    batiment = chambre.batiment
    chambre_service.delete_chambre(chambre)
    if batiment:
        batiment.sync_nombre_chambres()

    return Response({"message": "Chambre supprimée avec succès"}, status=status.HTTP_200_OK)

