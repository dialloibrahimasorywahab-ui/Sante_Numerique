from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from common.validators import validate_phone_number, validate_date_not_in_future
from .models import User


class UserSerializers(serializers.ModelSerializer):
    telephone = serializers.CharField(validators=[validate_phone_number], required=False)
    date_naissance = serializers.DateField(validators=[validate_date_not_in_future], required=False, allow_null=True)
    dateNaissance = serializers.DateField(source="date_naissance", validators=[validate_date_not_in_future], required=False, allow_null=True)
    mot_de_passe_hash = serializers.CharField(write_only=True, required=False, allow_blank=True)
    motDePasseHash = serializers.CharField(source="mot_de_passe_hash", write_only=True, required=False, allow_blank=True)
    idUser = serializers.IntegerField(source="id_user", read_only=True)
    derniere_connexion = serializers.DateTimeField(read_only=True)
    derniereConnexion = serializers.DateTimeField(source="derniere_connexion", read_only=True)
    idPatient = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    idMedecin = serializers.SerializerMethodField()
    medecin_id = serializers.SerializerMethodField()
    idPersonnel = serializers.SerializerMethodField()
    personnel_id = serializers.SerializerMethodField()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_idPatient(self, obj):
        if hasattr(obj, 'patient') and obj.patient:
            return obj.patient.id_patient
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_patient_id(self, obj):
        return self.get_idPatient(obj)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_idMedecin(self, obj):
        if hasattr(obj, 'medecin') and obj.medecin:
            return obj.medecin.id_medecin
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_medecin_id(self, obj):
        return self.get_idMedecin(obj)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_idPersonnel(self, obj):
        if hasattr(obj, 'personnel') and obj.personnel:
            return obj.personnel.id_personnel
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_personnel_id(self, obj):
        return self.get_idPersonnel(obj)

    class Meta:
        model = User
        fields = [
            'id_user',
            'idUser',
            'nom',
            'prenom',
            'email',
            'telephone',
            'login',
            'mot_de_passe_hash',
            'motDePasseHash',
            'role',
            'date_naissance',
            'dateNaissance',
            'actif',
            'derniere_connexion',
            'derniereConnexion',
            'idPatient',
            'patient_id',
            'idMedecin',
            'medecin_id',
            'idPersonnel',
            'personnel_id',
        ]
        extra_kwargs = {
            'role': {'required': False},
            'actif': {'required': False},
        }

    def to_internal_value(self, data):
        """
        Intercepte les clés alternatives envoyées par le client (motDePasse, password, dateNaissance, idUser)
        avant que la validation par champ ne s'exécute.
        """
        if isinstance(data, dict):
            data = data.copy()
            # Unification du champ mot de passe
            for key in ["motDePasse", "password", "mot_de_passe"]:
                if key in data and "mot_de_passe_hash" not in data and "motDePasseHash" not in data:
                    data["mot_de_passe_hash"] = data[key]
                    break
            # Unification de dateNaissance -> date_naissance
            if "dateNaissance" in data and "date_naissance" not in data:
                data["date_naissance"] = data["dateNaissance"]
            # Unification de idUser -> id_user
            if "idUser" in data and "id_user" not in data:
                data["id_user"] = data["idUser"]
        return super().to_internal_value(data)

    def _is_admin_request(self):
        request = self.context.get("request")
        return bool(
            request
            and hasattr(request, "user")
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == User.Role.ADMINISTRATEUR
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
        is_already_hashed = False
        if raw_pwd:
            try:
                identify_hasher(raw_pwd)
                is_already_hashed = True
            except (ValueError, Exception):
                is_already_hashed = False

        if raw_pwd and not is_already_hashed:
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
    Accepte les clés en français (snake_case et camelCase) et les alias en anglais pour compatibilité frontend.
    """
    ancien_mot_de_passe = serializers.CharField(write_only=True, required=False)
    ancienMotDePasse = serializers.CharField(write_only=True, required=False)
    oldPassword = serializers.CharField(write_only=True, required=False)

    nouveau_mot_de_passe = serializers.CharField(write_only=True, required=False)
    nouveauMotDePasse = serializers.CharField(write_only=True, required=False)
    newPassword = serializers.CharField(write_only=True, required=False)

    confirmation = serializers.CharField(write_only=True, required=False)
    confirmation_mot_de_passe = serializers.CharField(write_only=True, required=False)
    confirmationMotDePasse = serializers.CharField(write_only=True, required=False)
    confirmPassword = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        ancien = (
            attrs.get("ancien_mot_de_passe")
            or attrs.get("ancienMotDePasse")
            or attrs.get("oldPassword")
        )
        nouveau = (
            attrs.get("nouveau_mot_de_passe")
            or attrs.get("nouveauMotDePasse")
            or attrs.get("newPassword")
        )
        conf = (
            attrs.get("confirmation_mot_de_passe")
            or attrs.get("confirmationMotDePasse")
            or attrs.get("confirmation")
            or attrs.get("confirmPassword")
        )

        errors = {}
        if not ancien:
            errors["ancien_mot_de_passe"] = ["L'ancien mot de passe est obligatoire."]
            errors["ancienMotDePasse"] = ["L'ancien mot de passe est obligatoire."]
        if not nouveau:
            errors["nouveau_mot_de_passe"] = ["Le nouveau mot de passe est obligatoire."]
            errors["nouveauMotDePasse"] = ["Le nouveau mot de passe est obligatoire."]
        if not conf:
            errors["confirmation_mot_de_passe"] = ["La confirmation du mot de passe est obligatoire."]
            errors["confirmationMotDePasse"] = ["La confirmation du mot de passe est obligatoire."]
            errors["confirmation"] = ["La confirmation du mot de passe est obligatoire."]

        if errors:
            raise serializers.ValidationError(errors)

        if nouveau != conf:
            err_msg = ["Le nouveau mot de passe et sa confirmation ne correspondent pas."]
            raise serializers.ValidationError(
                {
                    "confirmation": err_msg,
                    "confirmation_mot_de_passe": err_msg,
                    "confirmationMotDePasse": err_msg,
                }
            )

        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.check_password(ancien):
            raise serializers.ValidationError(
                {
                    "ancien_mot_de_passe": ["L'ancien mot de passe fourni est incorrect."],
                    "ancienMotDePasse": ["L'ancien mot de passe fourni est incorrect."],
                }
            )

        if ancien == nouveau:
            raise serializers.ValidationError(
                {
                    "nouveau_mot_de_passe": ["Le nouveau mot de passe doit être différent de l'ancien."],
                    "nouveauMotDePasse": ["Le nouveau mot de passe doit être différent de l'ancien."],
                }
            )

        if user:
            try:
                validate_password(nouveau, user=user)
            except DjangoValidationError as e:
                raise serializers.ValidationError({
                    "nouveau_mot_de_passe": list(e.messages),
                    "nouveauMotDePasse": list(e.messages),
                })

        attrs["nouveau_mot_de_passe_valide"] = nouveau
        attrs["nouveauMotDePasse"] = nouveau
        attrs["nouveau_mot_de_passe"] = nouveau
        return attrs


class ResetPasswordAdminSerializer(serializers.Serializer):
    """
    Sérialiseur permettant à un ADMINISTRATEUR de réinitialiser le mot de passe d'un utilisateur.
    """
    nouveau_mot_de_passe = serializers.CharField(write_only=True, required=False)
    nouveauMotDePasse = serializers.CharField(write_only=True, required=False)
    newPassword = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        nouveau = (
            attrs.get("nouveau_mot_de_passe")
            or attrs.get("nouveauMotDePasse")
            or attrs.get("newPassword")
        )
        errors = {}
        if not nouveau:
            errors["nouveauMotDePasse"] = ["Le nouveau mot de passe est obligatoire."]

        if errors:
            raise serializers.ValidationError(errors)

        user = self.context.get("target_user")
        if user:
            try:
                validate_password(nouveau, user=user)
            except DjangoValidationError as e:
                raise serializers.ValidationError({"nouveauMotDePasse": list(e.messages)})

        attrs["nouveau_mot_de_passe_valide"] = nouveau
        attrs["nouveauMotDePasse"] = nouveau
        attrs["nouveau_mot_de_passe"] = nouveau
        return attrs
