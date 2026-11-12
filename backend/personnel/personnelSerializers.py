# pyrefly: ignore [missing-import]
from rest_framework import serializers
# pyrefly: ignore [missing-import]
from .models import Personnel


class PersonnelSerializer(serializers.ModelSerializer):
    idPersonnel = serializers.IntegerField(source="id_personnel", read_only=True)
    idUtilisateur = serializers.PrimaryKeyRelatedField(source="id_utilisateur", read_only=True)
    idService = serializers.PrimaryKeyRelatedField(source="id_service", read_only=True)
    nom = serializers.CharField(source="id_utilisateur.nom", required=False)
    prenom = serializers.CharField(source="id_utilisateur.prenom", required=False)
    email = serializers.EmailField(source="id_utilisateur.email", required=False)
    telephone = serializers.CharField(source="id_utilisateur.telephone", required=False)
    dateNaissance = serializers.DateField(source="id_utilisateur.date_naissance", required=False, allow_null=True)

    login = serializers.CharField(write_only=True, required=False)
    motDePasse = serializers.CharField(write_only=True, required=False)

    nomService = serializers.CharField(source="id_service.get_nom_service_display", read_only=True, required=False)

    typePersonnel = serializers.ChoiceField(choices=Personnel.TypePersonnel.choices, source="type_personnel", required=False)
    serviceHopital = serializers.CharField(source="service_hopital", required=False)
    telephonePro = serializers.CharField(source="telephone_pro", required=False, allow_null=True, allow_blank=True)
    emailPro = serializers.EmailField(source="email_pro", required=False, allow_null=True, allow_blank=True)
    dateEmbauche = serializers.DateField(source="date_embauche", required=False, allow_null=True)

    class Meta:
        model = Personnel
        fields = [
            "idPersonnel",
            "idUtilisateur",
            "idService",
            "nomService",
            "nom",
            "prenom",
            "email",
            "telephone",
            "dateNaissance",
            "login",
            "motDePasse",
            "matricule",
            "typePersonnel",
            "poste",
            "serviceHopital",
            "telephonePro",
            "emailPro",
            "dateEmbauche",
        ]
        extra_kwargs = {
            "idUtilisateur": {"required": False, "allow_null": True},
            "idService": {"required": False, "allow_null": True},
            "dateEmbauche": {"required": False},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            type_p = data.get("typePersonnel") or data.get("type_personnel")
            if type_p in ("AIDE_SOIGNANT", "Aide-Soignant(e)", "aide_soignant"):
                data["typePersonnel"] = "AUTRE"
                data["type_personnel"] = "AUTRE" 
            if 'mot_de_passe' in data and 'motDePasse' not in data:
                data['motDePasse'] = data['mot_de_passe']
            elif 'motDePasse' in data and 'mot_de_passe' not in data:
                data['mot_de_passe'] = data['motDePasse']
            if 'type_personnel' in data and 'typePersonnel' not in data:
                data['typePersonnel'] = data['type_personnel']
            if 'service_hopital' in data and 'serviceHopital' not in data:
                data['serviceHopital'] = data['service_hopital']
            if 'date_embauche' in data and 'dateEmbauche' not in data:
                data['dateEmbauche'] = data['date_embauche']
            if 'telephone_pro' in data and 'telephonePro' not in data:
                data['telephonePro'] = data['telephone_pro']
            if 'email_pro' in data and 'emailPro' not in data:
                data['emailPro'] = data['email_pro']
            if 'date_naissance' in data and 'dateNaissance' not in data:
                data['dateNaissance'] = data['date_naissance']
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
