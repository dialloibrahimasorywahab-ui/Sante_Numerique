from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from common.validators import validate_phone_number, validate_date_not_in_future
from .models import User


class UserSerializers(serializers.ModelSerializer):
    telephone = serializers.CharField(validators=[validate_phone_number], required=False)
    date_naissance = serializers.DateField(validators=[validate_date_not_in_future], required=False, allow_null=True)
    dateNaissance = serializers.DateField(source="date_naissance", validators=[validate_date_not_in_future], required=False, allow_null=True)
    mot_de_passe_hash = serializers.CharField(write_only=True, required=False, allow_blank=True)
    motDePasseHash = serializers.CharField(source="mot_de_passe_hash", write_only=True, required=False, allow_blank=True)
    idUser = serializers.IntegerField(source="id_user", read_only=True)
    derniereConnexion = serializers.DateTimeField(source="derniere_connexion", read_only=True)
    idPatient = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    idMedecin = serializers.SerializerMethodField()
    medecin_id = serializers.SerializerMethodField()
    idPersonnel = serializers.SerializerMethodField()
    personnel_id = serializers.SerializerMethodField()

    def get_idPatient(self, obj):
        if hasattr(obj, 'patient') and obj.patient:
            return obj.patient.id_patient
        return None

    def get_patient_id(self, obj):
        return self.get_idPatient(obj)

    def get_idMedecin(self, obj):
        if hasattr(obj, 'medecin') and obj.medecin:
            return obj.medecin.id_medecin
        return None

    def get_medecin_id(self, obj):
        return self.get_idMedecin(obj)

    def get_idPersonnel(self, obj):
        if hasattr(obj, 'personnel') and obj.personnel:
            return obj.personnel.id_personnel
        return None

    def get_personnel_id(self, obj):
        return self.get_idPersonnel(obj)

    class Meta:
        model = User
        fields = [
            "id_user",
            "idUser",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "mot_de_passe_hash",
            "motDePasseHash",
            "role",
            "derniere_connexion",
            "derniereConnexion",
            "date_naissance",
            "dateNaissance",
            "actif",
            "idPatient",
            "patient_id",
            "idMedecin",
            "medecin_id",
            "idPersonnel",
            "personnel_id",
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            pwd = data.get("password") or data.get("motDePasse") or data.get("mot_de_passe") or data.get("motDePasseHash")
            if pwd:
                data["mot_de_passe_hash"] = pwd
            if "dateNaissance" in data and "date_naissance" not in data:
                data["date_naissance"] = data["dateNaissance"]
        return super().to_internal_value(data)

    def _is_admin_request(self):
        """True si la requête provient d'un administrateur authentifié."""
        request = self.context.get("request")
        return (
            request is not None
            and getattr(request, "user", None) is not None
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMINISTRATEUR"
        )

    def validate(self, attrs):
        is_admin = self._is_admin_request()

        if not self.instance:
            # ---- CRÉATION ----
            # Si un non-admin tente de s'attribuer un rôle, on le force systématiquement à PATIENT
            if not is_admin:
                attrs["role"] = User.Role.PATIENT

            # Champs obligatoires à la création
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            if not any(
                self.initial_data.get(k)
                for k in ["mot_de_passe_hash", "motDePasseHash", "motDePasse", "mot_de_passe", "password"]
            ):
                errors["motDePasse"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)

        else:
            # ---- MISE À JOUR ----
            # CORRECTION PROBLÈME 2 & PROBLÈME 5 :
            # - Le rôle ne doit JAMAIS être modifié par un non-admin. Rejet explicite si modification tentée.
            # - Le statut actif/inactif ne peut être modifié que par un administrateur.
            # - Une valeur interdite ne doit jamais être acceptée silencieusement.
            if not is_admin:
                if "role" in self.initial_data and self.initial_data.get("role") != self.instance.role:
                    raise serializers.ValidationError({"role": "Seul un administrateur peut modifier le rôle d'un compte."})
                attrs.pop("role", None)

                if "actif" in self.initial_data and bool(self.initial_data.get("actif")) != bool(self.instance.actif):
                    raise serializers.ValidationError({"actif": "Seul un administrateur peut modifier le statut actif d'un compte."})
                attrs.pop("actif", None)

                if any(k in self.initial_data for k in ["id_user", "idUser"]):
                    val = str(self.initial_data.get("id_user") or self.initial_data.get("idUser"))
                    if val != str(self.instance.pk):
                        raise serializers.ValidationError({"id_user": "L'identifiant d'un compte utilisateur ne peut pas être modifié."})
                attrs.pop("id_user", None)
                attrs.pop("idUser", None)

        # Validation du mot de passe via validate_password de Django
        errors = {}
        raw_pwd = attrs.get("mot_de_passe_hash")
        if raw_pwd and not raw_pwd.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
            login_val = attrs.get("login", getattr(self.instance, "login", "") if self.instance else "")
            email_val = attrs.get("email", getattr(self.instance, "email", "") if self.instance else "")
            nom_val = attrs.get("nom", getattr(self.instance, "nom", "") if self.instance else "")
            prenom_val = attrs.get("prenom", getattr(self.instance, "prenom", "") if self.instance else "")
            user_obj = self.instance or User(
                login=login_val,
                email=email_val,
                nom=nom_val,
                prenom=prenom_val,
            )
            try:
                validate_password(raw_pwd, user=user_obj)
            except DjangoValidationError as e:
                errors["motDePasse"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        """
        Protection finale en couche défense-en-profondeur :
        même si validate() a laissé passer des champs sensibles,
        on les retire ici avant de les persister.
        """
        is_admin = self._is_admin_request()
        if not is_admin:
            validated_data.pop("role", None)
            validated_data.pop("actif", None)
            validated_data.pop("id_user", None)
            validated_data.pop("idUser", None)
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Sérialiseur pour le changement de mot de passe sécurisé par l'utilisateur connecté.
    Accepte les clés en français et les alias en anglais pour compatibilité frontend.
    """
    ancienMotDePasse = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="Mot de passe actuel de l'utilisateur"
    )
    nouveauMotDePasse = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="Nouveau mot de passe conforme aux règles de sécurité"
    )
    confirmationMotDePasse = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirmation du nouveau mot de passe"
    )

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "old_password" in data and "ancienMotDePasse" not in data:
                data["ancienMotDePasse"] = data["old_password"]
            elif "ancien_mot_de_passe" in data and "ancienMotDePasse" not in data:
                data["ancienMotDePasse"] = data["ancien_mot_de_passe"]

            if "new_password" in data and "nouveauMotDePasse" not in data:
                data["nouveauMotDePasse"] = data["new_password"]
            elif "nouveau_mot_de_passe" in data and "nouveauMotDePasse" not in data:
                data["nouveauMotDePasse"] = data["nouveau_mot_de_passe"]

            if "confirm_password" in data and "confirmationMotDePasse" not in data:
                data["confirmationMotDePasse"] = data["confirm_password"]
            elif "confirmation_mot_de_passe" in data and "confirmationMotDePasse" not in data:
                data["confirmationMotDePasse"] = data["confirmation_mot_de_passe"]
            elif "confirmation" in data and "confirmationMotDePasse" not in data:
                data["confirmationMotDePasse"] = data["confirmation"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError({"detail": "Utilisateur non authentifié."})

        user = request.user
        ancien = attrs.get("ancienMotDePasse")
        nouveau = attrs.get("nouveauMotDePasse")
        confirmation = attrs.get("confirmationMotDePasse")

        errors = {}
        if not user.check_password(ancien):
            errors["ancienMotDePasse"] = ["L'ancien mot de passe est incorrect."]

        if nouveau != confirmation:
            errors["confirmationMotDePasse"] = ["Les deux nouveaux mots de passe ne correspondent pas."]

        try:
            validate_password(nouveau, user=user)
        except DjangoValidationError as e:
            errors["nouveauMotDePasse"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
