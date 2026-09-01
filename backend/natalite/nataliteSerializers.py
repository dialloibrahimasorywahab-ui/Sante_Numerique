# pyrefly: ignore [missing-import]
from datetime import date
# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Natalite
from patients.models import Patient
from patients.patientSerializers import PatientSerializer
from medecin.models import Medecin
from medecin.medecinSerializers import MedecinSerializer


class NataliteSerializer(serializers.ModelSerializer):
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
        model = Natalite
        fields = [
            'id_nouveau_ne',
            'id_patient',
            'patient_detail',
            'id_medecin',
            'medecin_detail',
            'prenom_nouveau_ne',
            'nom_nouveau_ne',
            'date_naissance',
            'heure_naissance',
            'sexe',
            'groupe_sanguin',
            'poids',
            'taille',
            'lieu_naissance',
            'observation',
        ]
        read_only_fields = ['id_nouveau_ne']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if 'patient_id' in data and 'id_patient' not in data:
                data['id_patient'] = data['patient_id']
            if 'medecin_id' in data and 'id_medecin' not in data:
                data['id_medecin'] = data['medecin_id']
        return super().to_internal_value(data)

    def validate_date_naissance(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("La date de naissance ne peut pas être dans le futur.")
        return value

    def validate(self, attrs):
        patient = attrs.get('id_patient')
        if not patient and self.instance:
            patient = self.instance.id_patient

        if patient and getattr(patient, 'sexe', None):
            sexe_code = str(patient.sexe).upper()
            if sexe_code not in ('F', 'FEMININ'):
                raise serializers.ValidationError(
                    {"id_patient": "La patiente associée à une déclaration de naissance doit être de sexe féminin."}
                )

        poids = attrs.get('poids')
        taille = attrs.get('taille')
        if poids is not None:
            try:
                p = float(poids)
                if p < 0.3 or p > 7.0:
                    raise serializers.ValidationError({"poids": "Le poids du nouveau-né doit être compris entre 0.3 kg et 7.0 kg."})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"poids": "Poids du nouveau-né invalide."})

        if taille is not None:
            try:
                t = float(taille)
                if t < 20.0 or t > 70.0:
                    raise serializers.ValidationError({"taille": "La taille du nouveau-né doit être comprise entre 20.0 cm et 70.0 cm."})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"taille": "Taille du nouveau-né invalide."})

        return attrs


# Alias pour rétrocompatibilité en cas d'ancienne dépendance avec l'orthographe "Serialiszer"
NataliteSerialiszer = NataliteSerializer