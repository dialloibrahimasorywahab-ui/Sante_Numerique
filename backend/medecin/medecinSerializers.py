from rest_framework import serializers
from common.validators import validate_phone_number, validate_numero_ordre
from .models import Medecin, DisponibiliteMedecin, IndisponibiliteMedecin


class MedecinSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        if not self.instance and not attrs.get("idUtilisateur"):
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login", "motDePasse"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
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
    dureeCreneau = serializers.IntegerField(source="duree_creneau", required=False)

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
            "duree_creneau",
            "dureeCreneau",
            "actif",
        ]
        extra_kwargs = {
            "medecin": {"required": False},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "jourSemaine" in data and "jour_semaine" not in data:
                data["jour_semaine"] = data["jourSemaine"]
            if "heureDebut" in data and "heure_debut" not in data:
                data["heure_debut"] = data["heureDebut"]
            if "heureFin" in data and "heure_fin" not in data:
                data["heure_fin"] = data["heureFin"]
            if "pauseDebut" in data and "pause_debut" not in data:
                data["pause_debut"] = data["pauseDebut"]
            if "pauseFin" in data and "pause_fin" not in data:
                data["pause_fin"] = data["pauseFin"]
            if "dureeCreneau" in data and "duree_creneau" not in data:
                data["duree_creneau"] = data["dureeCreneau"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        h_debut = attrs.get("heure_debut") or getattr(self.instance, "heure_debut", None)
        h_fin = attrs.get("heure_fin") or getattr(self.instance, "heure_fin", None)
        if h_debut and h_fin and h_debut >= h_fin:
            raise serializers.ValidationError({"heure_fin": "L'heure de fin doit être postérieure à l'heure de début."})
        p_deb = attrs.get("pause_debut", getattr(self.instance, "pause_debut", None))
        p_fin = attrs.get("pause_fin", getattr(self.instance, "pause_fin", None))
        if p_deb and p_fin and p_deb >= p_fin:
            raise serializers.ValidationError({"pause_fin": "La fin de pause doit être postérieure au début de pause."})
        return attrs


class IndisponibiliteMedecinSerializer(serializers.ModelSerializer):
    dateDebut = serializers.DateField(source="date_debut", required=False)
    dateFin = serializers.DateField(source="date_fin", required=False)
    touteLaJournee = serializers.BooleanField(source="toute_la_journee", required=False)
    heureDebut = serializers.TimeField(source="heure_debut", required=False, allow_null=True)
    heureFin = serializers.TimeField(source="heure_fin", required=False, allow_null=True)

    class Meta:
        model = IndisponibiliteMedecin
        fields = [
            "id",
            "medecin",
            "date_debut",
            "dateDebut",
            "date_fin",
            "dateFin",
            "toute_la_journee",
            "touteLaJournee",
            "heure_debut",
            "heureDebut",
            "heure_fin",
            "heureFin",
            "motif",
            "actif",
        ]
        extra_kwargs = {
            "medecin": {"required": False},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "dateDebut" in data and "date_debut" not in data:
                data["date_debut"] = data["dateDebut"]
            if "dateFin" in data and "date_fin" not in data:
                data["date_fin"] = data["dateFin"]
            if "touteLaJournee" in data and "toute_la_journee" not in data:
                data["toute_la_journee"] = data["touteLaJournee"]
            if "heureDebut" in data and "heure_debut" not in data:
                data["heure_debut"] = data["heureDebut"]
            if "heureFin" in data and "heure_fin" not in data:
                data["heure_fin"] = data["heureFin"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        d_deb = attrs.get("date_debut") or getattr(self.instance, "date_debut", None)
        d_fin = attrs.get("date_fin") or getattr(self.instance, "date_fin", None)
        if d_deb and d_fin and d_deb > d_fin:
            raise serializers.ValidationError({"date_fin": "La date de fin ne peut pas précéder la date de début."})
        return attrs

