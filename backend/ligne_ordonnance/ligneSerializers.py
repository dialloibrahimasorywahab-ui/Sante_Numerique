from rest_framework import serializers
from .models import LigneOrdonnance


class LigneOrdonnanceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les lignes d'ordonnance avec support complet snake_case et camelCase.
    """
    idLigne = serializers.IntegerField(source='id', read_only=True)
    idOrdonnance = serializers.PrimaryKeyRelatedField(
        source='ordonnance',
        queryset=LigneOrdonnance._meta.get_field('ordonnance').remote_field.model.objects.all(),
        required=False,
        write_only=True
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

    def validate(self, attrs):
        # Synchronisation des variantes snake_case / camelCase
        if 'ordonnance' not in attrs and 'idOrdonnance' in self.initial_data:
            attrs['ordonnance'] = self.initial_data['idOrdonnance']
        if 'duree_traitement' not in attrs and 'dureeTraitement' in self.initial_data:
            attrs['duree_traitement'] = self.initial_data['dureeTraitement']
        return attrs
