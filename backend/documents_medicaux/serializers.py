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
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    titre = serializers.CharField(max_length=200)
    fichier = serializers.FileField()
    categorie = serializers.ChoiceField(
        choices=DocumentMedical.Categorie.choices,
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
