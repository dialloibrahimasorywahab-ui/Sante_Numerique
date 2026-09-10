from rest_framework import serializers
from .models import Ordonnance
from consultation.consultationSerializers import ConsultationSerializer
from ligne_ordonnance.ligneSerializers import LigneOrdonnanceSerializer


class OrdonnanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idOrdonnance = serializers.IntegerField(source='id', read_only=True)
    lignes = LigneOrdonnanceSerializer(many=True, required=False)

    class Meta:
        model = Ordonnance
        fields = [
            'id',
            'idOrdonnance',
            'consultation',
            'reference',
            'date_ordonnance',
            'observation',
            'lignes',
            'actif',
        ]
        extra_kwargs = {
            'reference': {'required': False},
            'date_ordonnance': {'required': False},
        }

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', None)
        ordonnance = Ordonnance.objects.create(**validated_data)
        if lignes_data:
            from ligne_ordonnance.models import LigneOrdonnance
            for l_data in lignes_data:
                LigneOrdonnance.objects.create(ordonnance=ordonnance, **l_data)
        return ordonnance


class OrdonnanceReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idOrdonnance = serializers.IntegerField(source='id', read_only=True)
    consultation_details = ConsultationSerializer(source='consultation', read_only=True)
    lignes = LigneOrdonnanceSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = [
            'id',
            'idOrdonnance',
            'consultation',
            'consultation_details',
            'reference',
            'date_ordonnance',
            'observation',
            'lignes',
            'actif',
        ]

