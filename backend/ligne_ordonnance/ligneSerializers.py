from rest_framework import serializers
from .models import LigneOrdonnance
from ordonnance.models import Ordonnance


class LigneOrdonnanceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les lignes d'ordonnance avec support complet snake_case et camelCase.
    """
    idLigne = serializers.IntegerField(source='id', read_only=True)
    idOrdonnance = serializers.PrimaryKeyRelatedField(
        queryset=Ordonnance.objects.all(),
        source='ordonnance',
        required=False
    )
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
            'ordonnance': {'required': False},
            'dosage': {'required': False, 'allow_blank': True, 'allow_null': True},
            'forme': {'required': False, 'allow_blank': True, 'allow_null': True},
            'duree_traitement': {'required': False, 'allow_blank': True, 'allow_null': True},
            'instructions': {'required': False, 'allow_blank': True, 'allow_null': True},
            'quantite': {'required': False, 'default': 1},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            # Prise en charge des variantes camelCase et snake_case pour l'ordonnance
            ord_val = (
                data.get('idOrdonnance')
                or data.get('id_ordonnance')
                or data.get('ordonnance')
                or data.get('ordonnance_id')
            )
            if ord_val is not None:
                data['ordonnance'] = ord_val
                data['idOrdonnance'] = ord_val

            # Prise en charge des variantes pour la durée de traitement
            duree_val = data.get('dureeTraitement') or data.get('duree_traitement')
            if duree_val is not None:
                data['duree_traitement'] = duree_val
                data['dureeTraitement'] = duree_val

        return super().to_internal_value(data)
