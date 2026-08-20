# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Batiment


class BatimentSerializer(serializers.ModelSerializer):
    totalChambresEffectif = serializers.IntegerField(source="total_chambres_effectif", read_only=True)

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
        if value < 0:
            raise serializers.ValidationError("Le nombre de chambres ne peut pas être négatif.")
        return value

