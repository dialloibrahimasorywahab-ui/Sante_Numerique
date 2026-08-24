# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.decorators import api_view
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
from .nataliteSerializers import NataliteSerializer
from .nataliteServices import NataliteService

# Instanciation du service de natalite 
natalite_service = NataliteService()


# Enregistrer un nouveau-né
@api_view(["POST"])
def create_naissance(request):
    serializer = NataliteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            natality = natalite_service.create_nouveaune(**serializer.validated_data)
            return Response(
                NataliteSerializer(natality).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Erreur lors de l'enregistrement du nouveau-né", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Récupération de tous les nouveaux-nés avec filtres
@api_view(["GET"])
def get_all_natality(request):
    patient_id = request.query_params.get('patient_id') or request.query_params.get('id_patient')
    medecin_id = request.query_params.get('medecin_id') or request.query_params.get('id_medecin')
    sexe = request.query_params.get('sexe')
    date_naissance = request.query_params.get('date') or request.query_params.get('date_naissance')
    search_q = request.query_params.get('search') or request.query_params.get('q')

    if patient_id:
        natalities = natalite_service.get_nouveaux_nes_by_patient(patient_id)
    elif medecin_id:
        natalities = natalite_service.get_nouveaux_nes_by_medecin(medecin_id)
    elif sexe:
        natalities = natalite_service.get_natalities_by_sexe(sexe)
    elif date_naissance:
        natalities = natalite_service.get_nouveaux_nes_by_date(date_naissance)
    elif search_q:
        natalities = natalite_service.search_nouveaux_nes(search_q)
    else:
        natalities = natalite_service.get_all_nouveau_ne()

    serializer = NataliteSerializer(natalities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Récupérer les nouveaux-nés par leur sexe 
@api_view(["GET"])
def get_natalities_by_sexe(request, sexe):
    natalities = natalite_service.get_natalities_by_sexe(sexe)
    serializer = NataliteSerializer(natalities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Afficher les nouveaux-nés d'une patiente (mère)
@api_view(["GET"])
def get_natalities_by_patient(request, patient_id):
    natalities = natalite_service.get_nouveaux_nes_by_patient(patient_id)
    serializer = NataliteSerializer(natalities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Afficher les nouveaux-nés d'un médecin superviseur
@api_view(["GET"])
def get_natalities_by_medecin(request, medecin_id):
    natalities = natalite_service.get_nouveaux_nes_by_medecin(medecin_id)
    serializer = NataliteSerializer(natalities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Afficher un nouveau-né par son ID
@api_view(["GET"])
def get_natality(request, id_natality):
    natality = natalite_service.get_nouveauneById(id_natality)
    if natality is None: 
        return Response({"message": "Aucune natalité correspondante"}, status=status.HTTP_404_NOT_FOUND)
    return Response(NataliteSerializer(natality).data, status=status.HTTP_200_OK)


# Mettre à jour les informations d'un nouveau-né 
@api_view(["PUT", "PATCH"])
def update_natality(request, natality_id):
    natality = natalite_service.get_nouveauneById(natality_id)
    if natality is None:
        return Response({"message": "Aucune natalité trouvée"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = NataliteSerializer(natality, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated = natalite_service.update_data_nouveau_ne(natality, **serializer.validated_data)
            return Response(NataliteSerializer(updated).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Erreur lors de la modification de la natalité", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Désactiver (soft delete) ou supprimer une fiche de natalité
@api_view(["DELETE"])
def delete_natality(request, natality_id):
    natality = natalite_service.get_nouveauneById(natality_id)
    if natality is None:
        return Response({"message": "Aucune natalité trouvée"}, status=status.HTTP_404_NOT_FOUND)

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    natalite_service.delete_nouveau_ne(natality, hard=hard)

    if hard:
        return Response({"message": "Fiche de natalité supprimée définitivement avec succès."}, status=status.HTTP_200_OK)
    return Response({"message": "Fiche de natalité désactivée (archivée) avec succès."}, status=status.HTTP_200_OK)

