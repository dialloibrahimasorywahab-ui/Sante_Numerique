from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .litSerializers import LitSerializer
from .litServices import LitService

lit_service = LitService()


@api_view(["POST"])
def create_lit(request):
    serializer = LitSerializer(data=request.data)
    if serializer.is_valid():
        try:
            lit = lit_service.create_lit(**serializer.validated_data)
            return Response(LitSerializer(lit).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Erreur lors de la création du lit.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_lits(request):
    chambre_id = request.query_params.get('chambre_id') or request.query_params.get('id_chambre')
    etat = request.query_params.get('etat')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if chambre_id:
        lits = lit_service.get_lits_by_chambre(chambre_id)
    elif etat:
        lits = lit_service.get_lits_by_etat(etat)
    elif search_q:
        lits = lit_service.search_lits(search_q)
    else:
        lits = lit_service.get_all_lits()

    serializer = LitSerializer(lits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_lits_by_etat(request, etat):
    lits = lit_service.get_lits_by_etat(etat)
    serializer = LitSerializer(lits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_lit(request, lit_id):

    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)
    return Response(LitSerializer(lit).data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def update_lit(request, lit_id):
    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = LitSerializer(lit, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = lit_service.update_lit(lit, **serializer.validated_data)
            return Response(LitSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Erreur lors de la modification.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_lit(request, lit_id):
    lit = lit_service.get_lit(lit_id)
    if lit is None:
        return Response({"message": "Lit introuvable"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    lit_service.delete_lit(lit, hard=hard)

    if hard:
        return Response({"message": "Lit supprimé définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Lit marqué comme hors service (archivé) avec succès."}, status=status.HTTP_200_OK)

