# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Ordonnance
from consultation.consultationSerializers import ConsultationSerializer


class OrdonnanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idOrdonnance = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Ordonnance
        fields = [
            'id',
            'idOrdonnance',
            'consultation',
            'reference',
            'date_ordonnance',
            'observation',
            'actif',
        ]
        extra_kwargs = {
            'reference': {'required': False},
            'date_ordonnance': {'required': False},
        }


class OrdonnanceReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idOrdonnance = serializers.IntegerField(source='id', read_only=True)
    consultation_details = ConsultationSerializer(source='consultation', read_only=True)

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
            'actif',
        ]
