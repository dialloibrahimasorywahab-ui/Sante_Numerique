from datetime import date
from rest_framework import serializers
from .models import Mortalite
from patients.models import Patient
from patients.patientSerializers import PatientSerializer
from medecin.models import Medecin
from medecin.medecinSerializers import MedecinSerializer


class MortaliteSerializer(serializers.ModelSerializer):
    id_patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        required=True,
    )
    patient_detail = PatientSerializer(source='id_patient', read_only=True)

    id_medecin = serializers.PrimaryKeyRelatedField(
        queryset=Medecin.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    medecin_detail = MedecinSerializer(source='id_medecin', read_only=True)

    class Meta:
        model = Mortalite
        fields = [
            'id_deces',
            'id_patient',
            'patient_detail',
            'id_medecin',
            'medecin_detail',
            'date_deces',
            'heure_deces',
            'cause_deces',
            'lieu_deces',
            'observation',
        ]
        read_only_fields = ['id_deces']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if 'patient_id' in data and 'id_patient' not in data:
                data['id_patient'] = data['patient_id']
            if 'medecin_id' in data and 'id_medecin' not in data:
                data['id_medecin'] = data['medecin_id']
        return super().to_internal_value(data)

    def validate_date_deces(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("La date de décès ne peut pas être dans le futur.")
        return value
