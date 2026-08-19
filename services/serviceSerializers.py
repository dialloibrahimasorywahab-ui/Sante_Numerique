from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    nomService = serializers.CharField(required=False)
    nomServiceDisplay = serializers.CharField(source="get_nomService_display", read_only=True)

    class Meta:
        model = Service
        fields = [
            "idService",
            "nomService",
            "nomServiceDisplay",
            "description",
            "bureauLocalisation",
            "actif",
        ]

    def validate_nomService(self, value):
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
            if not attrs.get("nomService") and not self.initial_data.get("nomService"):
                raise serializers.ValidationError({"nomService": ["Ce champ est obligatoire."]})
        return attrs
