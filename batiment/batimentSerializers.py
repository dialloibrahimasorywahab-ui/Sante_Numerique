# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Batiment


class BatimentSerializer(serializers.ModelSerializer):
    nombre_chambre = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=1000,
        default=None,
        help_text="Nombre prévisionnel de chambres (optionnel, null par défaut)."
    )
    totalChambresEffectif = serializers.IntegerField(
        source="total_chambres_effectif",
        read_only=True,
        allow_null=True,
        help_text="Nombre total de chambres effectives."
    )

    class Meta:
        model = Batiment
        fields = [
            'idBatiment',
            'nom',
            'description',
            'nombre_chambre',
            'totalChambresEffectif',
            'actif',
        ]

    def validate_nom(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Le nom du bâtiment ne peut pas être vide.")
        return str(value).strip()

    def validate_nombre_chambre(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Le nombre de chambres ne peut pas être négatif.")
        return value

