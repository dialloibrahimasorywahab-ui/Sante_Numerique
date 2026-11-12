from rest_framework import serializers
from .models import Ordonnance
from consultation.consultationSerializers import ConsultationSerializer, ConsultationReadSerializer
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
    consultation_details = ConsultationReadSerializer(source='consultation', read_only=True)
    lignes = LigneOrdonnanceSerializer(many=True, read_only=True)
    medecin_nom = serializers.SerializerMethodField()
    patient_nom = serializers.SerializerMethodField()

    class Meta:
        model = Ordonnance
        fields = [
            'id',
            'idOrdonnance',
            'consultation',
            'consultation_details',
            'medecin_nom',
            'patient_nom',
            'reference',
            'date_ordonnance',
            'observation',
            'lignes',
            'actif',
        ]

    def get_medecin_nom(self, obj):
        try:
            if obj.consultation and obj.consultation.medecin:
                m = obj.consultation.medecin
                user = getattr(m, 'id_utilisateur', None) or getattr(m, 'idUtilisateur', None)
                if user:
                    return f"Dr. {user.prenom or ''} {user.nom or ''}".strip()
        except Exception:
            pass
        return None

    def get_patient_nom(self, obj):
        try:
            if obj.consultation and obj.consultation.patient:
                p = obj.consultation.patient
                user = getattr(p, 'id_utilisateur', None) or getattr(p, 'idUtilisateur', None)
                if user:
                    return f"{user.prenom or ''} {user.nom or ''}".strip()
        except Exception:
            pass
        return None
