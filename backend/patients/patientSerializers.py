from rest_framework import serializers
from common.validators import (
    validate_phone_number,
    validate_date_not_in_future,
    validate_blood_group,
    generate_secure_password,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
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

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "groupeSanguin" in data and "groupe_sanguin" not in data:
                data["groupe_sanguin"] = data["groupeSanguin"]
            if "dateNaissance" in data and "date_naissance" not in data:
                data["date_naissance"] = data["dateNaissance"]
            if "numeroSecuriteSociale" in data and "numero_securite_sociale" not in data:
                data["numero_securite_sociale"] = data["numeroSecuriteSociale"]
            if "personneAContacter" in data and "personne_a_contacter" not in data:
                data["personne_a_contacter"] = data["personneAContacter"]
            if "dateInscription" in data and "date_inscription" not in data:
                data["date_inscription"] = data["dateInscription"]
            if "idUtilisateur" in data and "id_utilisateur" not in data:
                data["id_utilisateur"] = data["idUtilisateur"]
            if "motDePasse" in data and "mot_de_passe" not in data:
                data["mot_de_passe"] = data["motDePasse"]
        return super().to_internal_value(data)

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

            # Gestion du mot de passe : aucun mot de passe par défaut prévisible
            raw_password = (
                self.initial_data.get("mot_de_passe")
                or self.initial_data.get("motDePasse")
                or self.initial_data.get("password")
                or attrs.get("mot_de_passe")
            )
            if raw_password:
                temp_user = User(
                    login=attrs.get("login", "") or self.initial_data.get("login", ""),
                    email=attrs.get("email", "") or self.initial_data.get("email", ""),
                    nom=attrs.get("nom", "") or self.initial_data.get("nom", ""),
                    prenom=attrs.get("prenom", "") or self.initial_data.get("prenom", ""),
                )
                try:
                    validate_password(raw_password, user=temp_user)
                except DjangoValidationError as ve:
                    errors["mot_de_passe"] = list(ve.messages)
                attrs["mot_de_passe"] = raw_password
            else:
                attrs["mot_de_passe"] = generate_secure_password()

            if errors:
                raise serializers.ValidationError(errors)

        # Protection du numéro de sécurité sociale :
        # Un patient ne peut pas modifier lui-même son numéro de sécurité sociale (réservé aux médecins et admins)
        if self.instance and "numero_securite_sociale" in attrs:
            request = self.context.get("request")
            if request and getattr(request.user, "role", None) == "PATIENT":
                new_secu = attrs.get("numero_securite_sociale")
                old_secu = getattr(self.instance, "numero_securite_sociale", None)
                if new_secu != old_secu:
                    raise serializers.ValidationError({
                        "numero_securite_sociale": "Seul un médecin ou un administrateur est habilité à modifier le numéro de sécurité sociale."
                    })

        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Exposer les clés camelCase pour le frontend Angular
        ret["idPatient"] = ret.get("id_patient")
        ret["idUtilisateur"] = ret.get("id_utilisateur")
        ret["dateNaissance"] = ret.get("date_naissance")
        ret["sexeDisplay"] = instance.get_sexe_display() if hasattr(instance, "get_sexe_display") else ret.get("sexe")
        ret["groupeSanguin"] = ret.get("groupe_sanguin")
        ret["groupeSanguinDisplay"] = instance.get_groupe_sanguin_display() if hasattr(instance, "get_groupe_sanguin_display") else ret.get("groupe_sanguin")
        ret["numeroSecuriteSociale"] = ret.get("numero_securite_sociale")
        ret["personneAContacter"] = ret.get("personne_a_contacter")
        ret["dateInscription"] = ret.get("date_inscription")
        ret["actif"] = instance.id_utilisateur.actif if getattr(instance, "id_utilisateur", None) else True

        request = self.context.get("request")
        if request is not None:
            user = getattr(request, "user", None)
            is_staff_or_admin = (
                user
                and user.is_authenticated
                and getattr(user, "role", None) in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]
            )
            is_owner = False
            if user and user.is_authenticated:
                patient_user = getattr(instance, "id_utilisateur", None)
                if patient_user and (
                    patient_user == user
                    or getattr(patient_user, "id_user", None) == getattr(user, "id_user", None)
                ):
                    is_owner = True

            # Si l'utilisateur n'est ni personnel de santé ni le patient titulaire du dossier,
            # le numéro de sécurité sociale est masqué pour protéger cette donnée de santé sensible.
            if not (is_staff_or_admin or is_owner):
                ret["numero_securite_sociale"] = None
                ret["numeroSecuriteSociale"] = None

        return ret

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "ADMINISTRATEUR":
            validated_data.pop("id_utilisateur", None)
        return super().update(instance, validated_data)
