from rest_framework import serializers
from .models import Medecin


class MedecinSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="idUtilisateur.nom", required=False)
    prenom = serializers.CharField(source="idUtilisateur.prenom", required=False)
    email = serializers.EmailField(source="idUtilisateur.email", required=False)
    telephone = serializers.CharField(source="idUtilisateur.telephone", required=False)

    login = serializers.CharField(write_only=True, required=False)
    motDePasse = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Medecin
        fields = [
            "idMedecin",
            "idUtilisateur",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "motDePasse",
            "specialite",
            "matricule",
            "numeroOrdre",
            "telephonePro",
            "emailPro",
            "bureau",
            "dateEmbauche",
        ]
        extra_kwargs = {
            "idUtilisateur": {"required": False, "allow_null": True}
        }
