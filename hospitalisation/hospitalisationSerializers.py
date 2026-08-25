from rest_framework import serializers
from .models import Hospitalisation
from patients.patientSerializers import PatientSerializer
from medecin.medecinSerializers import MedecinSerializer
from lit.litSerializers import LitSerializer


class HospitalisationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idHospitalisation = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Hospitalisation
        fields = [
            'id',
            'idHospitalisation',
            'patient',
            'medecin',
            'lit',
            'date_entree',
            'date_sortie',
            'motif',
            'statut',
            'observation',
            'actif',
        ]

    def validate(self, attrs):
        date_entree = attrs.get('date_entree')
        date_sortie = attrs.get('date_sortie')
        if not date_entree and self.instance:
            date_entree = self.instance.date_entree
        if not date_sortie and self.instance:
            date_sortie = self.instance.date_sortie

        if date_entree and date_sortie and date_sortie < date_entree:
            raise serializers.ValidationError({
                "date_sortie": "La date de sortie ne peut pas être antérieure à la date d'entrée."
            })
        return attrs


class HospitalisationReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idHospitalisation = serializers.IntegerField(source='id', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    medecin_details = MedecinSerializer(source='medecin', read_only=True)
    lit_details = LitSerializer(source='lit', read_only=True)

    class Meta:
        model = Hospitalisation
        fields = [
            'id',
            'idHospitalisation',
            'patient',
            'patient_details',
            'medecin',
            'medecin_details',
            'lit',
            'lit_details',
            'date_entree',
            'date_sortie',
            'motif',
            'statut',
            'observation',
            'actif',
        ]
