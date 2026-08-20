# pyrefly: ignore [missing-import]
from rest_framework import serializers
# pyrefly: ignore [missing-import]
from .models import Personnel


class PersonnelSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="idUtilisateur.nom", required=False)
    prenom = serializers.CharField(source="idUtilisateur.prenom", required=False)
    email = serializers.EmailField(source="idUtilisateur.email", required=False)
    telephone = serializers.CharField(source="idUtilisateur.telephone", required=False)
    dateNaissance = serializers.DateField(source="idUtilisateur.dateNaissance", required=False, allow_null=True)

    login = serializers.CharField(write_only=True, required=False)
    motDePasse = serializers.CharField(write_only=True, required=False)

    nomService = serializers.CharField(source="idService.get_nomService_display", read_only=True, required=False)

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
