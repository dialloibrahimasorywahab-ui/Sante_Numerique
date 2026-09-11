# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Batiment


class BatimentSerializer(serializers.ModelSerializer):
    id_batiment = serializers.IntegerField(read_only=True)
    idBatiment = serializers.IntegerField(source="id_batiment", read_only=True)
    nombre_chambre = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=1000,
        default=0,
        help_text="Nombre prévisionnel de chambres (optionnel, 0 par défaut)."
    )
    total_chambres_effectif = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        help_text="Nombre total de chambres effectives."
    )
    totalChambresEffectif = serializers.IntegerField(
        source="total_chambres_effectif",
        read_only=True,
        allow_null=True,
        help_text="Nombre total de chambres effectives (alias camelCase)."
    )

    reference = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Batiment
        fields = [
            'id_batiment',
            'idBatiment',
            'reference',
            'nom',
            'description',
            'nombre_chambre',
            'total_chambres_effectif',
            'totalChambresEffectif',
            'actif',
        ]

    def get_reference(self, obj):
        return f"BAT-{obj.id_batiment:02d}"

    def validate_nom(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Le nom du bâtiment ne peut pas être vide.")
        return str(value).strip()

    def validate_nombre_chambre(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Le nombre de chambres ne peut pas être négatif.")
        return value
