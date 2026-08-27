from rest_framework import serializers
from common.validators import validate_strict_positive
from .models import FraisConsultation


class FraisConsultationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idFrais = serializers.IntegerField(source='id', read_only=True)
    montant = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_strict_positive]
    )
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
