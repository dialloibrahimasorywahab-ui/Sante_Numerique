from rest_framework import serializers
from .models import Sejour, DemandeAnalyse
from patients.patientSerializers import PatientSerializer
from services.serviceSerializers import ServiceSerializer
from medecin.medecinSerializers import MedecinSerializer


class DemandeAnalyseSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    sejour_reference = serializers.CharField(source="sejour.reference", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = DemandeAnalyse
        fields = [
            "id",
            "patient",
            "patient_id",
            "sejour",
            "sejour_reference",
            "prescripteur",
            "type_analyse",
            "date_prescription",
            "statut",
            "statut_display",
            "date_prelevement",
            "date_resultat",
            "commentaire",
            "actif",
        ]


class SejourReadSerializer(serializers.ModelSerializer):
    """Serializer complet en lecture pour les séjours."""
    patient_details = PatientSerializer(source="patient", read_only=True)
    service_details = ServiceSerializer(source="service_responsable", read_only=True)
    medecin_details = MedecinSerializer(source="medecin_responsable", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    type_prise_en_charge_display = serializers.CharField(source="get_type_prise_en_charge_display", read_only=True)
    localisation_actuelle_info = serializers.SerializerMethodField()

    class Meta:
        model = Sejour
        fields = [
            "id_sejour",
            "reference",
            "patient",
            "patient_details",
            "service_responsable",
            "service_details",
            "medecin_responsable",
            "medecin_details",
            "enregistre_par",
            "type_prise_en_charge",
            "type_prise_en_charge_display",
            "statut",
            "statut_display",
            "date_admission",
            "motif_admission",
            "date_sortie",
            "motif_sortie",
            "localisation_actuelle_info",
            "actif",
            "created_at",
            "updated_at",
        ]

    def get_localisation_actuelle_info(self, obj):
        loc = obj.localisation_actuelle
        if not loc:
            return None
        return {
            "id": loc.id,
            "service_id": loc.service_id,
            "service_nom": str(loc.service),
            "batiment_id": loc.batiment_id,
            "batiment_nom": loc.batiment.nom if loc.batiment else None,
            "chambre_id": loc.chambre_id,
            "chambre_numero": loc.chambre.numero_chambre if loc.chambre else None,
            "lit_id": loc.lit_id,
            "lit_numero": loc.lit.numero_lit if loc.lit else None,
            "date_debut": loc.date_debut,
        }


class SejourCreateSerializer(serializers.ModelSerializer):
    """Serializer d'admission d'un patient."""
    patient = serializers.IntegerField(required=True)
    service_responsable = serializers.IntegerField(required=True)
    medecin_responsable = serializers.IntegerField(required=False, allow_null=True)
    batiment = serializers.IntegerField(required=False, allow_null=True)
    chambre = serializers.IntegerField(required=False, allow_null=True)
    lit = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Sejour
        fields = [
            "reference",
            "patient",
            "service_responsable",
            "medecin_responsable",
            "batiment",
            "chambre",
            "lit",
            "type_prise_en_charge",
            "date_admission",
            "motif_admission",
        ]

    def validate(self, attrs):
        # Permettre la compatibilité camelCase et snake_case
        return attrs


class SejourSortieSerializer(serializers.Serializer):
    """Serializer pour enregistrer ou autoriser une sortie."""
    date_sortie = serializers.DateTimeField(required=False, allow_null=True)
    motif_sortie = serializers.CharField(required=True, allow_blank=False)
