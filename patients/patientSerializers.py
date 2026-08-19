from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="idUtilisateur.nom", required=False)
    prenom = serializers.CharField(source="idUtilisateur.prenom", required=False)
    email = serializers.EmailField(source="idUtilisateur.email", required=False)
    telephone = serializers.CharField(source="idUtilisateur.telephone", required=False)

    login = serializers.CharField(write_only=True, required=False)
    motDePasse = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Patient
        fields = [
            "idPatient",
            "idUtilisateur",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "motDePasse",
            "dateNaissance",
            "sexe",
            "adresse",
            "groupeSanguin",
            "numeroSecuriteSociale",
            "personneAContacter",
            "dateInscription",
        ]
        extra_kwargs = {
            "idUtilisateur": {"required": False, "allow_null": True},
            "dateInscription": {"required": False},
            "sexe": {"required": False},
            "adresse": {"required": False},
            "groupeSanguin": {"required": False},
            "numeroSecuriteSociale": {"required": False},
            "personneAContacter": {"required": False},
        }

    def validate(self, attrs):
        if not self.instance and not attrs.get("idUtilisateur"):
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login", "motDePasse"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

