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
