from rest_framework import serializers
from .models import LocalisationPatient
from services.serviceSerializers import ServiceSerializer
from batiment.batimentSerializers import BatimentSerializer
from chambre.chambreSerializers import ChambreSerializer
from lit.litSerializers import LitSerializer


class LocalisationReadSerializer(serializers.ModelSerializer):
    service_details = ServiceSerializer(source="service", read_only=True)
    batiment_details = BatimentSerializer(source="batiment", read_only=True)
    chambre_details = ChambreSerializer(source="chambre", read_only=True)
    lit_details = LitSerializer(source="lit", read_only=True)
    sejour_reference = serializers.CharField(source="sejour.reference", read_only=True)
    patient_id = serializers.IntegerField(source="sejour.patient.id_patient", read_only=True)
    patient_nom = serializers.CharField(source="sejour.patient.nom", read_only=True)
    patient_prenom = serializers.CharField(source="sejour.patient.prenom", read_only=True)
    patient_nss = serializers.CharField(source="sejour.patient.numero_securite_sociale", read_only=True)

    class Meta:
        model = LocalisationPatient
        fields = [
            "id",
            "sejour",
            "sejour_reference",
            "patient_id",
            "patient_nom",
            "patient_prenom",
            "patient_nss",
            "service",
            "service_details",
            "batiment",
            "batiment_details",
            "chambre",
            "chambre_details",
            "lit",
            "lit_details",
            "date_debut",
            "date_fin",
            "est_actuelle",
            "motif",
            "commentaire",
            "enregistre_par",
        ]


class LocalisationCreateSerializer(serializers.ModelSerializer):
    sejour = serializers.IntegerField(required=True)
    service = serializers.IntegerField(required=True)
    batiment = serializers.IntegerField(required=False, allow_null=True)
    chambre = serializers.IntegerField(required=False, allow_null=True)
    lit = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = LocalisationPatient
        fields = [
            "sejour",
            "service",
            "batiment",
            "chambre",
            "lit",
            "date_debut",
            "motif",
            "commentaire",
        ]
