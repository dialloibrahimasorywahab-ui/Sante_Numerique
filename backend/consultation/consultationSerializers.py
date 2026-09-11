from rest_framework import serializers
from .models import Consultation
from patients.patientSerializers import PatientSerializer
from medecin.medecinSerializers import MedecinSerializer
from rendezvous.rendezvousSerializers import RendezVousSerializer
from frais_consultation.fraisSerializers import FraisConsultationSerializer


class ConsultationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idConsultation = serializers.IntegerField(source='id', read_only=True)
    montant_frais = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Montant des frais de consultation saisi par le médecin"
    )
    description_frais = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        write_only=True,
        help_text="Description ou motif des frais"
    )

    class Meta:
        model = Consultation
        fields = [
            'id',
            'idConsultation',
            'patient',
            'medecin',
            'rdv',
            'frais',
            'montant_frais',
            'description_frais',
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
