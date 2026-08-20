# pyrefly: ignore [missing-import]
from django.db import IntegrityError
# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.decorators import api_view
# pyrefly: ignore [missing-import]
from rest_framework.response import Response

from .batimentSerializers import BatimentSerializer
from .batimentServices import BatimentService
from chambre.chambreSerializers import ChambreSerializer

batiment_service = BatimentService()


@api_view(["POST"])
def create_batiment(request):
    serializer = BatimentSerializer(data=request.data)
    if serializer.is_valid():
        try:
            batiment = batiment_service.create_batiment(**serializer.validated_data)
            return Response(BatimentSerializer(batiment).data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"error": "Un bâtiment avec ce nom existe déjà.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_batiments(request):
    query = request.query_params.get("search") or request.query_params.get("q")
    if query:
        batiments = batiment_service.search_batiments(query)
    else:
        batiments = batiment_service.get_all_batiments()
    serializer = BatimentSerializer(batiments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_batiment(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(BatimentSerializer(batiment).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_batiment_chambres(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)

    chambres = batiment.chambres.all()
    serializer = ChambreSerializer(chambres, many=True)
    return Response(
        {
            "batiment": BatimentSerializer(batiment).data,
            "chambres": serializer.data,
            "total_chambres": chambres.count()
        },
        status=status.HTTP_200_OK
    )


@api_view(["PUT", "PATCH"])
def update_batiment(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = BatimentSerializer(batiment, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = batiment_service.update_batiment(batiment, **serializer.validated_data)
            return Response(BatimentSerializer(updated).data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": "Erreur d'intégrité.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_batiment(request, batiment_id):
    batiment = batiment_service.get_batiment(batiment_id)
    if batiment is None:
        return Response({"message": "Bâtiment introuvable"}, status=status.HTTP_404_NOT_FOUND)
    batiment_service.delete_batiment(batiment)
    return Response({"message": "Bâtiment supprimé avec succès"}, status=status.HTTP_200_OK)

