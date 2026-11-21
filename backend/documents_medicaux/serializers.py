from rest_framework import serializers
from .models import DocumentMedical
from patients.models import Patient
from medecin.models import Medecin
from consultation.models import Consultation


class DocumentMedicalSerializer(serializers.ModelSerializer):
    patient_nom = serializers.SerializerMethodField()
    patient_prenom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentMedical
        fields = [
            'id_document',
            'idDocument',
            'patient',
            'patient_nom',
            'patient_prenom',
            'medecin',
            'medecin_nom',
            'consultation',
            'titre',
            'categorie',
            'categorie_display',
            'nom_original',
            'taille_octets',
            'type_mime',
            'checksum_sha256',
            'chiffre',
            'date_document',
            'date_upload',
            'observation',
            'download_url',
            'actif',
        ]
        read_only_fields = [
            'id_document',
            'nom_original',
            'taille_octets',
            'type_mime',
            'checksum_sha256',
            'chiffre',
            'date_upload',
        ]

    def get_patient_nom(self, obj) -> str:
        if obj.patient and obj.patient.id_utilisateur:
            return obj.patient.id_utilisateur.nom
        return ""

    def get_patient_prenom(self, obj) -> str:
        if obj.patient and obj.patient.id_utilisateur:
            return obj.patient.id_utilisateur.prenom
        return ""

    def get_medecin_nom(self, obj) -> str:
        if obj.medecin and obj.medecin.id_utilisateur:
            return f"Dr. {obj.medecin.id_utilisateur.prenom} {obj.medecin.id_utilisateur.nom}"
        return ""

    def get_download_url(self, obj) -> str:
        request = self.context.get('request')
        relative_url = f"/documents_medicaux/{obj.id_document}/download/"
        if request:
            return request.build_absolute_uri(relative_url)
        return relative_url


class DocumentUploadSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        required=False,
        allow_null=True
    )
    titre = serializers.CharField(max_length=200)
    fichier = serializers.FileField()
    categorie = serializers.CharField(
        max_length=50,
        default=DocumentMedical.Categorie.AUTRE,
        required=False
    )
    medecin = serializers.PrimaryKeyRelatedField(
        queryset=Medecin.objects.all(),
        required=False,
        allow_null=True
    )
    consultation = serializers.PrimaryKeyRelatedField(
        queryset=Consultation.objects.all(),
        required=False,
        allow_null=True
    )
    date_document = serializers.DateField(required=False, allow_null=True)
    observation = serializers.CharField(required=False, allow_blank=True, default="")

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            data = data.dict()
        elif hasattr(data, 'copy'):
            data = data.copy()
        elif isinstance(data, dict):
            data = dict(data)

        # 1. Alias de fichier (fichier, file, document)
        if 'fichier' not in data:
            if 'file' in data:
                data['fichier'] = data['file']
            elif 'document' in data:
                data['fichier'] = data['document']

        # 2. Alias de patient (patient, idPatient, patientId, id_patient, patient_id)
        if 'patient' not in data or data.get('patient') in [None, '', 'undefined', 'null']:
            for k in ['idPatient', 'patientId', 'id_patient', 'patient_id', 'id_user', 'idUser']:
                if k in data and data[k] not in [None, '', 'undefined', 'null']:
                    data['patient'] = data[k]
                    break

        # 3. Résolution patient si passé sous forme d'id_utilisateur au lieu d'id_patient
        pat_val = data.get('patient')
        if pat_val not in [None, '', 'undefined', 'null']:
            try:
                p_id = int(pat_val)
                if not Patient.objects.filter(id_patient=p_id).exists():
                    p_from_user = Patient.objects.filter(id_utilisateur_id=p_id).first()
                    if p_from_user:
                        data['patient'] = p_from_user.id_patient
            except (ValueError, TypeError):
                pass

        # 4. Alias date_document (dateDocument, date)
        if 'date_document' not in data or data.get('date_document') in [None, '', 'undefined', 'null']:
            if 'dateDocument' in data and data['dateDocument']:
                data['date_document'] = data['dateDocument']
            elif 'date' in data and data['date']:
                data['date_document'] = data['date']

        return super().to_internal_value(data)

    def validate_categorie(self, value):
        if not value:
            return DocumentMedical.Categorie.AUTRE
        val_upper = str(value).upper().strip()
        if val_upper in DocumentMedical.Categorie.values:
            return val_upper
        return DocumentMedical.Categorie.AUTRE
