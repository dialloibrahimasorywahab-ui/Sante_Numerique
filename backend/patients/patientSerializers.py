from rest_framework import serializers
from common.validators import (
    validate_phone_number,
    validate_date_not_in_future,
    validate_blood_group,
)
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="id_utilisateur.nom", required=False)
    prenom = serializers.CharField(source="id_utilisateur.prenom", required=False)
    email = serializers.EmailField(source="id_utilisateur.email", required=False)
    telephone = serializers.CharField(
        source="id_utilisateur.telephone",
        validators=[validate_phone_number],
        required=False
    )
    date_naissance = serializers.DateField(
        validators=[validate_date_not_in_future],
        required=False,
        allow_null=True
    )
    dateNaissance = serializers.DateField(
        source="date_naissance",
        validators=[validate_date_not_in_future],
        required=False,
        allow_null=True
    )
    numero_securite_sociale = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    numeroSecuriteSociale = serializers.CharField(
        source="numero_securite_sociale",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    groupe_sanguin = serializers.CharField(
        validators=[validate_blood_group],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    groupeSanguin = serializers.CharField(
        source="groupe_sanguin",
        validators=[validate_blood_group],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    personne_a_contacter = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    personneAContacter = serializers.CharField(
        source="personne_a_contacter",
        required=False,
        allow_blank=True,
        allow_null=True
    )
    date_inscription = serializers.DateField(required=False)
    dateInscription = serializers.DateField(source="date_inscription", required=False)

    idPatient = serializers.IntegerField(source="id_patient", read_only=True)
    idUtilisateur = serializers.PrimaryKeyRelatedField(source="id_utilisateur", read_only=True)

    login = serializers.CharField(write_only=True, required=False)
    motDePasse = serializers.CharField(write_only=True, required=False)
    mot_de_passe = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Patient
        fields = [
            "id_patient",
            "idPatient",
            "id_utilisateur",
            "idUtilisateur",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "motDePasse",
            "mot_de_passe",
            "date_naissance",
            "dateNaissance",
            "sexe",
            "adresse",
            "groupe_sanguin",
            "groupeSanguin",
            "numero_securite_sociale",
            "numeroSecuriteSociale",
            "personne_a_contacter",
            "personneAContacter",
            "date_inscription",
            "dateInscription",
        ]
        extra_kwargs = {
            "id_utilisateur": {"required": False, "allow_null": True},
            "date_inscription": {"required": False},
            "sexe": {"required": False},
            "adresse": {"required": False},
            "personne_a_contacter": {"required": False},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "idUtilisateur" in data and "id_utilisateur" not in data:
                data["id_utilisateur"] = data["idUtilisateur"]
            if "dateNaissance" in data and "date_naissance" not in data:
                data["date_naissance"] = data["dateNaissance"]
            if "groupeSanguin" in data and "groupe_sanguin" not in data:
                data["groupe_sanguin"] = data["groupeSanguin"]
            if "numeroSecuriteSociale" in data and "numero_securite_sociale" not in data:
                data["numero_securite_sociale"] = data["numeroSecuriteSociale"]
            if "personneAContacter" in data and "personne_a_contacter" not in data:
                data["personne_a_contacter"] = data["personneAContacter"]
            if "dateInscription" in data and "date_inscription" not in data:
                data["date_inscription"] = data["dateInscription"]
            if "motDePasse" in data and "mot_de_passe" not in data:
                data["mot_de_passe"] = data["motDePasse"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        id_user = attrs.get("id_utilisateur")
        if not self.instance and (not id_user or isinstance(id_user, dict)):
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            if not self.initial_data.get("motDePasse") and not self.initial_data.get("mot_de_passe") and not self.initial_data.get("password"):
                errors["motDePasse"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "ADMINISTRATEUR":
            validated_data.pop("id_utilisateur", None)
            validated_data.pop("idUtilisateur", None)
        return super().update(instance, validated_data)
