from rest_framework import serializers
from .models import Consultation
from patients.patientSerializers import PatientSerializer
from medecin.medecinSerializers import MedecinSerializer
from rendezvous.rendezvousSerializers import RendezVousSerializer
from frais_consultation.fraisSerializers import FraisConsultationSerializer


class ConsultationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idConsultation = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id',
            'idConsultation',
            'patient',
            'medecin',
            'rdv',
            'frais',
            'date_cons',
            'symptomes',
            'diagnostic',
            'observations',
            'actif',
        ]


class ConsultationReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idConsultation = serializers.IntegerField(source='id', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    medecin_details = MedecinSerializer(source='medecin', read_only=True)
    rdv_details = RendezVousSerializer(source='rdv', read_only=True)
    frais_details = FraisConsultationSerializer(source='frais', read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id',
            'idConsultation',
            'patient',
            'patient_details',
            'medecin',
            'medecin_details',
            'rdv',
            'rdv_details',
            'frais',
            'frais_details',
            'date_cons',
            'symptomes',
            'diagnostic',
            'observations',
            'actif',
        ]
