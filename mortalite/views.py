from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .mortaliteSerializers import MortaliteSerializer
from .mortaliteServices import MortaliteService

mortalite_service = MortaliteService()


@api_view(["POST"])
def create_deces(request):
    serializer = MortaliteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            deces = mortalite_service.create_deces(**serializer.validated_data)
            return Response(
                MortaliteSerializer(deces).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la création de la fiche de décès", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_mortalite(request):
    patient_id = request.query_params.get('patient_id') or request.query_params.get('id_patient')
    medecin_id = request.query_params.get('medecin_id') or request.query_params.get('id_medecin')
    date_deces = request.query_params.get('date') or request.query_params.get('date_deces')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if patient_id:
        mortalites = mortalite_service.get_mortalites_by_patient(patient_id)
    elif medecin_id:
        mortalites = mortalite_service.get_mortalites_by_medecin(medecin_id)
    elif date_deces:
        mortalites = mortalite_service.get_mortalites_by_date(date_deces)
    elif search_q:
        mortalites = mortalite_service.search_mortalites(search_q)
    else:
        mortalites = mortalite_service.get_all_mortalites()

    serializer = MortaliteSerializer(mortalites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_mortalite(request, id_deces):
    deces = mortalite_service.get_deces_by_id(id_deces)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(MortaliteSerializer(deces).data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def update_mortalite(request, deces_id):
    deces = mortalite_service.get_deces_by_id(deces_id)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = MortaliteSerializer(deces, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = mortalite_service.update_deces(deces, **serializer.validated_data)
            return Response(MortaliteSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la modification", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_mortalite(request, deces_id):
    deces = mortalite_service.get_deces_by_id(deces_id)
    if deces is None:
        return Response({"message": "Fiche de décès introuvable"}, status=status.HTTP_404_NOT_FOUND)

    mortalite_service.delete_deces(deces)
    return Response({"message": "Fiche de décès supprimée avec succès"}, status=status.HTTP_200_OK)
