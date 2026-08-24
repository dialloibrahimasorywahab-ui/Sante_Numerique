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

    def validate_date_rdv(self, value):
        from datetime import date
        if not self.instance and value < date.today():
            raise serializers.ValidationError("La date du rendez-vous ne peut pas être dans le passé.")
        return value

    def validate(self, attrs):
        if not self.instance:
            if 'patient' not in attrs:
                raise serializers.ValidationError({"id_patient": "Le champ id_patient est obligatoire."})
            if 'medecin' not in attrs:
                raise serializers.ValidationError({"id_medecin": "Le champ id_medecin est obligatoire."})

        medecin = attrs.get('medecin') or (self.instance.medecin if self.instance else None)
        date_rdv = attrs.get('date_rdv') or (self.instance.date_rdv if self.instance else None)
        heure = attrs.get('heure') or (self.instance.heure if self.instance else None)

        # Past Datetime Validation (Date + Heure)
        if not self.instance and date_rdv and heure:
            from datetime import datetime
            rdv_datetime = datetime.combine(date_rdv, heure)
            if rdv_datetime < datetime.now():
                raise serializers.ValidationError({"heure": "L'heure du rendez-vous est déjà passée."})


        # Anti Double-Booking Validation
        if medecin and date_rdv and heure:
            conflict_qs = RendezVous.objects.filter(
                medecin=medecin,
                date_rdv=date_rdv,
                heure=heure
            ).exclude(statut=RendezVous.StatutRendezVous.ANNULE)

            if self.instance:
                conflict_qs = conflict_qs.exclude(id=self.instance.id)

            if conflict_qs.exists():
                raise serializers.ValidationError({
                    "heure": f"Le médecin Dr. {medecin.idUtilisateur.prenom} {medecin.idUtilisateur.nom} a déjà un rendez-vous à cette date ({date_rdv}) et heure ({heure})."
                })

        return attrs


