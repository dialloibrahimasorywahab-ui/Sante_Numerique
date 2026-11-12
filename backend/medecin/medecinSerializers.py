from rest_framework import serializers
from common.validators import validate_phone_number, validate_numero_ordre
from .models import Medecin, DisponibiliteMedecin, IndisponibiliteMedecin


class MedecinSerializer(serializers.ModelSerializer):
    idMedecin = serializers.IntegerField(source="id_medecin", read_only=True)
    idUtilisateur = serializers.IntegerField(source="id_utilisateur.id_user", required=False, allow_null=True)
    nom = serializers.CharField(source="id_utilisateur.nom", required=False)
    prenom = serializers.CharField(source="id_utilisateur.prenom", required=False)
    email = serializers.EmailField(source="id_utilisateur.email", required=False)
    telephone = serializers.CharField(
        source="id_utilisateur.telephone",
        validators=[validate_phone_number],
        required=False
    )
    specialiteDisplay = serializers.CharField(source="get_specialite_display", read_only=True)
    telephonePro = serializers.CharField(
        source="telephone_pro",
        validators=[validate_phone_number],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    emailPro = serializers.EmailField(
        source="email_pro",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    numeroOrdre = serializers.CharField(
        source="numero_ordre",
        validators=[validate_numero_ordre],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    dateEmbauche = serializers.DateField(
        source="date_embauche",
        required=False,
        allow_null=True
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
            "specialiteDisplay",
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

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            spec = data.get("specialite")
            if spec in ("MEDECINE_GENERALE", "Médecine Générale", "medecine_generale", "GENERAL"):
                data["specialite"] = "GENERALISTE" 
            if 'mot_de_passe' in data and 'motDePasse' not in data:
                data['motDePasse'] = data['mot_de_passe']
            elif 'motDePasse' in data and 'mot_de_passe' not in data:
                data['mot_de_passe'] = data['motDePasse']
            if 'numero_ordre' in data and 'numeroOrdre' not in data:
                data['numeroOrdre'] = data['numero_ordre']
            if 'date_embauche' in data and 'dateEmbauche' not in data:
                data['dateEmbauche'] = data['date_embauche']
            if 'telephone_pro' in data and 'telephonePro' not in data:
                data['telephonePro'] = data['telephone_pro']
            if 'email_pro' in data and 'emailPro' not in data:
                data['emailPro'] = data['email_pro']
        return super().to_internal_value(data)

    def validate(self, attrs):
        if not self.instance and not attrs.get("idUtilisateur") and not attrs.get("id_utilisateur"):
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            mot_de_passe = (
                self.initial_data.get("motDePasse")
                or self.initial_data.get("mot_de_passe")
                or self.initial_data.get("password")
                or self.initial_data.get("motDePasseHash")
                or self.initial_data.get("mot_de_passe_hash")
                or attrs.get("motDePasse")
                or attrs.get("mot_de_passe")
            )
            if not mot_de_passe:
                errors["motDePasse"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "ADMINISTRATEUR":
            validated_data.pop("idUtilisateur", None)
        return super().update(instance, validated_data)


class DisponibiliteMedecinSerializer(serializers.ModelSerializer):
    jourSemaineDisplay = serializers.CharField(source="get_jour_semaine_display", read_only=True)
    jourSemaine = serializers.IntegerField(source="jour_semaine", required=False)
    heureDebut = serializers.TimeField(source="heure_debut", required=False)
    heureFin = serializers.TimeField(source="heure_fin", required=False)
    pauseDebut = serializers.TimeField(source="pause_debut", required=False, allow_null=True)
    pauseFin = serializers.TimeField(source="pause_fin", required=False, allow_null=True)
    duree_creneau = serializers.IntegerField(source="duree_consultation", required=False)
    dureeCreneau = serializers.IntegerField(source="duree_consultation", required=False)
    dureeConsultation = serializers.IntegerField(source="duree_consultation", required=False)

    class Meta:
        model = DisponibiliteMedecin
        # The serializer exposes snake_case and camelCase aliases for the same
        # model fields, so DRF cannot build its automatic unique-together validator.
        validators = []
        fields = [
            "id",
            "medecin",
            "jour_semaine",
            "jourSemaine",
            "jourSemaineDisplay",
            "heure_debut",
            "heureDebut",
            "heure_fin",
            "heureFin",
            "pause_debut",
            "pauseDebut",
            "pause_fin",
            "pauseFin",
            "duree_consultation",
            "dureeConsultation",
            "duree_creneau",
            "dureeCreneau",
            "actif",
        ]
        extra_kwargs = {
            "jour_semaine": {"required": False},
            "heure_debut": {"required": False},
            "heure_fin": {"required": False},
            "duree_consultation": {"required": False},
        }

    def validate(self, attrs):
        for camel, snake in [
            ("jourSemaine", "jour_semaine"),
            ("heureDebut", "heure_debut"),
            ("heureFin", "heure_fin"),
            ("pauseDebut", "pause_debut"),
            ("pauseFin", "pause_fin"),
            ("dureeCreneau", "duree_creneau"),
        ]:
            if snake not in attrs and camel in self.initial_data:
                attrs[snake] = self.initial_data[camel]

        jour = attrs.get("jour_semaine") or (self.instance.jour_semaine if self.instance else None)
        debut = attrs.get("heure_debut") or (self.instance.heure_debut if self.instance else None)
        fin = attrs.get("heure_fin") or (self.instance.heure_fin if self.instance else None)

        if not self.instance:
            errors = {}
            if jour is None:
                errors["jourSemaine"] = ["Ce champ est obligatoire."]
            if debut is None:
                errors["heureDebut"] = ["Ce champ est obligatoire."]
            if fin is None:
                errors["heureFin"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)

        if debut and fin and fin <= debut:
            raise serializers.ValidationError({"heureFin": "L'heure de fin doit être postérieure à l'heure de début."})

        pause_d = attrs.get("pause_debut", self.instance.pause_debut if self.instance else None)
        pause_f = attrs.get("pause_fin", self.instance.pause_fin if self.instance else None)
        if pause_d and pause_f and pause_f <= pause_d:
            raise serializers.ValidationError({"pauseFin": "L'heure de fin de pause doit être postérieure à l'heure de début de pause."})

        return attrs


class IndisponibiliteMedecinSerializer(serializers.ModelSerializer):
    dateDebut = serializers.DateTimeField(source="date_debut", required=False)
    dateFin = serializers.DateTimeField(source="date_fin", required=False)
    motif = serializers.CharField(source="titre", required=False, allow_blank=True)
    typeIndisponibilite = serializers.CharField(source="type_indisponibilite", required=False)

    class Meta:
        model = IndisponibiliteMedecin
        fields = [
            "id",
            "medecin",
            "type_indisponibilite",
            "typeIndisponibilite",
            "date_debut",
            "dateDebut",
            "date_fin",
            "dateFin",
            "motif",
        ]
        extra_kwargs = {
            "date_debut": {"required": False},
            "date_fin": {"required": False},
        }

    def validate(self, attrs):
        if "date_debut" not in attrs and "dateDebut" in self.initial_data:
            attrs["date_debut"] = self.initial_data["dateDebut"]
        if "date_fin" not in attrs and "dateFin" in self.initial_data:
            attrs["date_fin"] = self.initial_data["dateFin"]

        debut = attrs.get("date_debut") or (self.instance.date_debut if self.instance else None)
        fin = attrs.get("date_fin") or (self.instance.date_fin if self.instance else None)

        if not self.instance:
            errors = {}
            if debut is None:
                errors["dateDebut"] = ["Ce champ est obligatoire."]
            if fin is None:
                errors["dateFin"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)

        if debut and fin and fin <= debut:
            raise serializers.ValidationError({"dateFin": "La date de fin d'indisponibilité doit être postérieure à la date de début."})
        return attrs
