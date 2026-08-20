# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import RendezVous
from patients.models import Patient
from patients.patientSerializers import PatientSerializer
from medecin.models import Medecin
from medecin.medecinSerializers import MedecinSerializer


class RendezVousSerializer(serializers.ModelSerializer):
    id_patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=False
    )
    id_medecin = serializers.PrimaryKeyRelatedField(
        queryset=Medecin.objects.all(),
        source='medecin',
        write_only=True,
        required=False
    )

    patient_detail = PatientSerializer(source='patient', read_only=True)
    medecin_detail = MedecinSerializer(source='medecin', read_only=True)
    statutDisplay = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = RendezVous
        fields = [
            'id',
            'idRendezVous',
            'id_patient',
            'patient_detail',
            'id_medecin',
            'medecin_detail',
            'date_rdv',
            'heure',
            'motif',
            'statut',
            'statutDisplay',
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if 'patient_id' in data and 'id_patient' not in data:
                data['id_patient'] = data['patient_id']
            if 'medecin_id' in data and 'id_medecin' not in data:
                data['id_medecin'] = data['medecin_id']
        return super().to_internal_value(data)

    def validate(self, attrs):
        if not self.instance:
            if 'patient' not in attrs:
                raise serializers.ValidationError({"id_patient": "Le champ id_patient est obligatoire."})
            if 'medecin' not in attrs:
                raise serializers.ValidationError({"id_medecin": "Le champ id_medecin est obligatoire."})
        return attrs
