from rest_framework import serializers
from common.validators import (
    validate_phone_number,
    validate_date_not_in_future,
    validate_blood_group,
)
from users.models import User
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
    numero_securite_sociale = serializers.CharField(
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
    adresse = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    personne_a_contacter = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    date_inscription = serializers.DateField(required=False)

    id_patient = serializers.IntegerField(read_only=True)
    id_utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    login = serializers.CharField(write_only=True, required=False)
    mot_de_passe = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Patient
        fields = [
            "id_patient",
            "id_utilisateur",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "mot_de_passe",
            "date_naissance",
            "sexe",
            "adresse",
            "groupe_sanguin",
            "numero_securite_sociale",
            "personne_a_contacter",
            "date_inscription",
        ]
        extra_kwargs = {
            "id_utilisateur": {"required": False, "allow_null": True},
            "date_inscription": {"required": False},
            "sexe": {"required": False},
            "adresse": {"required": False},
            "personne_a_contacter": {"required": False},
        }

    def validate(self, attrs):
        id_user = attrs.get("id_utilisateur")
        if not self.instance and (not id_user or isinstance(id_user, dict)):
            errors = {}
            for field in ["nom", "prenom", "email", "telephone"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            
            # Gestion intelligente du login
            if not self.initial_data.get("login") and not attrs.get("login"):
                email = self.initial_data.get("email") or ""
                nom = self.initial_data.get("nom") or ""
                prenom = self.initial_data.get("prenom") or ""
                if email:
                    attrs["login"] = email.split("@")[0].lower()
                elif nom and prenom:
                    attrs["login"] = f"{prenom.lower()}_{nom.lower()}"
                else:
                    errors["login"] = ["Ce champ est obligatoire."]
            elif self.initial_data.get("login"):
                attrs["login"] = self.initial_data.get("login")

            # Gestion du mot de passe
            if not self.initial_data.get("mot_de_passe") and not self.initial_data.get("motDePasse") and not self.initial_data.get("password") and not attrs.get("mot_de_passe"):
                attrs["mot_de_passe"] = "PatientPass123!"
            elif self.initial_data.get("mot_de_passe"):
                attrs["mot_de_passe"] = self.initial_data.get("mot_de_passe")
            elif self.initial_data.get("motDePasse"):
                attrs["mot_de_passe"] = self.initial_data.get("motDePasse")

            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "ADMINISTRATEUR":
            validated_data.pop("id_utilisateur", None)
        return super().update(instance, validated_data)
