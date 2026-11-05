from rest_framework import serializers
from .models import LigneOrdonnance


class LigneOrdonnanceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les lignes d'ordonnance avec support complet snake_case et camelCase.
    """
    idLigne = serializers.IntegerField(source='id', read_only=True)
    idOrdonnance = serializers.IntegerField(source='ordonnance_id', read_only=True)
    dureeTraitement = serializers.CharField(source='duree_traitement', required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = LigneOrdonnance
        fields = [
            'id',
            'idLigne',
            'ordonnance',
            'idOrdonnance',
            'medicament',
            'dosage',
            'forme',
            'posologie',
            'duree_traitement',
            'dureeTraitement',
            'quantite',
            'instructions',
            'actif',
        ]
        extra_kwargs = {
            'dosage': {'required': False, 'allow_blank': True, 'allow_null': True},
            'forme': {'required': False, 'allow_blank': True, 'allow_null': True},
            'duree_traitement': {'required': False, 'allow_blank': True, 'allow_null': True},
            'instructions': {'required': False, 'allow_blank': True, 'allow_null': True},
            'quantite': {'required': False, 'default': 1},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if 'idOrdonnance' in data and 'ordonnance' not in data:
                data['ordonnance'] = data['idOrdonnance']
            if 'dureeTraitement' in data and 'duree_traitement' not in data:
                data['duree_traitement'] = data['dureeTraitement']
        return super().to_internal_value(data)
