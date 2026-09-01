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

    def validate(self, attrs):
        request = self.context.get("request")
        is_admin = request and getattr(request, "user", None) and request.user.is_authenticated and getattr(request.user, "role", None) == "ADMINISTRATEUR"
        if not is_admin:
            attrs["role"] = User.Role.PATIENT

        errors = {}
        if not self.instance:
            for field in ["nom", "prenom", "email", "telephone", "login"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            if not self.initial_data.get("mot_de_passe_hash") and not self.initial_data.get("motDePasseHash") and not self.initial_data.get("motDePasse") and not self.initial_data.get("mot_de_passe") and not self.initial_data.get("password"):
                errors["motDePasse"] = ["Ce champ est obligatoire."]

        # Validation de mot de passe via validate_password de Django
        raw_pwd = attrs.get("mot_de_passe_hash")
        if raw_pwd and not raw_pwd.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
            user_obj = self.instance or User(
                login=attrs.get("login", getattr(self.instance, "login", "")),
                email=attrs.get("email", getattr(self.instance, "email", "")),
                nom=attrs.get("nom", getattr(self.instance, "nom", "")),
                prenom=attrs.get("prenom", getattr(self.instance, "prenom", "")),
            )
            try:
                validate_password(raw_pwd, user=user_obj)
            except DjangoValidationError as e:
                errors["motDePasse"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "ADMINISTRATEUR":
            validated_data.pop("role", None)
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