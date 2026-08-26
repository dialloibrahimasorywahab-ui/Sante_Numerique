# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Chambre
from batiment.models import Batiment
from batiment.batimentSerializers import BatimentSerializer


class ChambreSerializer(serializers.ModelSerializer):
    id_batiment = serializers.PrimaryKeyRelatedField(
        queryset=Batiment.objects.all(),
        source='batiment',
        write_only=True,
        required=False
    )
    numero_chambre = serializers.IntegerField(
        default=0,
        min_value=0,
        help_text="Numéro de la chambre (par défaut 0)."
    )
    capacite = serializers.IntegerField(
        default=1,
        min_value=1,
        max_value=50,
        help_text="Capacité / nombre de lits dans la chambre (par défaut 1)."
    )
    batiment_detail = BatimentSerializer(source='batiment', read_only=True)
    typeChambreDisplay = serializers.CharField(source="get_type_chambre_display", read_only=True)
    statutDisplay = serializers.CharField(source="get_statut_display", read_only=True)
    litsDisponiblesCount = serializers.IntegerField(source="lits_disponibles_count", read_only=True)
    litsOccupesCount = serializers.IntegerField(source="lits_occupes_count", read_only=True)

    class Meta:
        model = Chambre
        fields = [
            'id',
            'idChambre',
            'id_batiment',
            'batiment_detail',
            'numero_chambre',
            'type_chambre',
            'typeChambreDisplay',
            'capacite',
            'statut',
            'statutDisplay',
            'litsDisponiblesCount',
            'litsOccupesCount',
        ]


    def to_internal_value(self, data):
        if isinstance(data, dict):
            if 'batiment_id' in data and 'id_batiment' not in data:
                data = data.copy()
                data['id_batiment'] = data['batiment_id']
        return super().to_internal_value(data)

    def validate_capacite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacité (nombre de lits) doit être supérieure à 0.")
        return value

    def validate(self, attrs):
        if not self.instance and 'batiment' not in attrs:
            raise serializers.ValidationError({"id_batiment": "Le champ id_batiment est obligatoire."})
        return attrs


