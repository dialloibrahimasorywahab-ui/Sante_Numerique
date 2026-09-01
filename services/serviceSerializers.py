from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    idService = serializers.IntegerField(source="id_service", read_only=True)
    nom_service = serializers.CharField(required=False)
    nomService = serializers.CharField(source="nom_service", required=False)
    nom_service_display = serializers.CharField(source="get_nom_service_display", read_only=True)
    nomServiceDisplay = serializers.CharField(source="get_nom_service_display", read_only=True)
    bureau_localisation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bureauLocalisation = serializers.CharField(source="bureau_localisation", required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Service
        fields = [
            "id_service",
            "idService",
            "nom_service",
            "nomService",
            "nom_service_display",
            "nomServiceDisplay",
            "description",
            "bureau_localisation",
            "bureauLocalisation",
            "actif",
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "nomService" in data and "nom_service" not in data:
                data["nom_service"] = data["nomService"]
            if "bureauLocalisation" in data and "bureau_localisation" not in data:
                data["bureau_localisation"] = data["bureauLocalisation"]
        return super().to_internal_value(data)

    def validate_nom_service(self, value):
        if not value:
            return value

        clean_val = str(value).strip()

        # 1. Correspondance exacte clé ou libellé
        for key, label in Service.NomService.choices:
            if clean_val.upper() == key.upper() or clean_val.lower() == label.lower():
                return key

        # 2. Correspondance partielle / tolérante
        for key, label in Service.NomService.choices:
            if clean_val.lower() in label.lower() or label.lower() in clean_val.lower() or clean_val.upper() in key:
                return key

        valid_labels = [f"'{c[1]}' ({c[0]})" for c in Service.NomService.choices]
        raise serializers.ValidationError(
            f"\"{value}\" n'est pas un nom de service valide. Choix valides: {', '.join(valid_labels)}"
        )

    def validate(self, attrs):
        if not self.instance:
            if not attrs.get("nom_service") and not self.initial_data.get("nom_service") and not self.initial_data.get("nomService"):
                raise serializers.ValidationError({"nom_service": ["Ce champ est obligatoire."]})
        return attrs
