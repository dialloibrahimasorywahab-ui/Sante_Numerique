from rest_framework import serializers
from .models import FraisConsultation


class FraisConsultationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idFrais = serializers.IntegerField(source='id', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = FraisConsultation
        fields = [
            'id',
            'idFrais',
            'montant',
            'description',
            'date_paiement',
            'statut',
            'statut_display',
            'actif',
        ]

    def validate_montant(self, value):
        if value < 0:
            raise serializers.ValidationError("Le montant ne peut pas être négatif.")
        return value
