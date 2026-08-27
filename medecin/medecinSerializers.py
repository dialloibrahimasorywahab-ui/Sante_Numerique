from rest_framework import serializers
from common.validators import validate_phone_number, validate_numero_ordre
from .models import Medecin


class MedecinSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="idUtilisateur.nom", required=False)
    prenom = serializers.CharField(source="idUtilisateur.prenom", required=False)
    email = serializers.EmailField(source="idUtilisateur.email", required=False)
    telephone = serializers.CharField(
        source="idUtilisateur.telephone",
        validators=[validate_phone_number],
        required=False
    )
    telephonePro = serializers.CharField(
        validators=[validate_phone_number],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    numeroOrdre = serializers.CharField(
        validators=[validate_numero_ordre],
        required=False,
        allow_null=True,
        allow_blank=True
    )

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
            "idUtilisateur": {"required": False, "allow_null": True},
            "dateEmbauche": {"required": False},
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
