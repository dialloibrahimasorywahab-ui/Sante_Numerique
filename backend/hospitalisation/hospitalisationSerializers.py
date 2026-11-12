import re
from rest_framework import serializers
from .models import Hospitalisation
from patients.patientSerializers import PatientSerializer
from medecin.medecinSerializers import MedecinSerializer
from lit.litSerializers import LitSerializer


class HospitalisationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idHospitalisation = serializers.IntegerField(source='id', read_only=True)
    id_admission = serializers.IntegerField(source='id', read_only=True)

    # Permettre la création directe d'un nouveau patient lors de la première admission
    nouveau_patient = serializers.BooleanField(required=False, default=False)
    nom = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    prenom = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    telephone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    sexe = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    adresse = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    groupe_sanguin = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    numero_securite_sociale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personne_a_contacter = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Champs médicaux d'admission
    priorite = serializers.ChoiceField(
        choices=['NORMAL', 'URGENT', 'TRES_URGENT'],
        default='NORMAL',
        required=False
    )
    symptomes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    diagnostic_provisoire = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    service_nom = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    antecedents = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    traitements_en_cours = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Hospitalisation
        fields = [
            'id',
            'idHospitalisation',
            'id_admission',
            'patient',
            'medecin',
            'lit',
            'date_entree',
            'date_sortie',
            'motif',
            'statut',
            'observation',
            'actif',
            'nouveau_patient',
            'nom',
            'prenom',
            'telephone',
            'email',
            'date_naissance',
            'sexe',
            'adresse',
            'groupe_sanguin',
            'numero_securite_sociale',
            'personne_a_contacter',
            'priorite',
            'symptomes',
            'diagnostic_provisoire',
            'service_nom',
            'antecedents',
            'allergies',
            'traitements_en_cours',
        ]
        extra_kwargs = {
            'patient': {'required': False, 'allow_null': True},
            'medecin': {'required': False, 'allow_null': True},
            'lit': {'required': False, 'allow_null': True},
            'date_sortie': {'required': False, 'allow_null': True},
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if 'nouveauPatient' in data and 'nouveau_patient' not in data:
                data['nouveau_patient'] = data['nouveauPatient']
            if 'dateNaissance' in data and 'date_naissance' not in data:
                data['date_naissance'] = data['dateNaissance']
            if 'dateEntree' in data and 'date_entree' not in data:
                data['date_entree'] = data['dateEntree']
            if 'dateSortie' in data and 'date_sortie' not in data:
                data['date_sortie'] = data['dateSortie']
            if 'groupeSanguin' in data and 'groupe_sanguin' not in data:
                data['groupe_sanguin'] = data['groupeSanguin']
            if 'numeroSecuriteSociale' in data and 'numero_securite_sociale' not in data:
                data['numero_securite_sociale'] = data['numeroSecuriteSociale']
            if 'personneAContacter' in data and 'personne_a_contacter' not in data:
                data['personne_a_contacter'] = data['personneAContacter']
            if 'diagnosticProvisoire' in data and 'diagnostic_provisoire' not in data:
                data['diagnostic_provisoire'] = data['diagnosticProvisoire']
            if 'serviceNom' in data and 'service_nom' not in data:
                data['service_nom'] = data['serviceNom']
            if 'service' in data and 'service_nom' not in data:
                data['service_nom'] = str(data['service'])
            if 'traitementsEnCours' in data and 'traitements_en_cours' not in data:
                data['traitements_en_cours'] = data['traitementsEnCours']
            if 'idPatient' in data and 'patient' not in data:
                data['patient'] = data['idPatient']
            if 'idMedecin' in data and 'medecin' not in data:
                data['medecin'] = data['idMedecin']
            if 'idLit' in data and 'lit' not in data:
                data['lit'] = data['idLit']
        return super().to_internal_value(data)

    def validate(self, attrs):
        is_nouveau = attrs.get('nouveau_patient', False) or (not attrs.get('patient') and bool(attrs.get('nom')))

        if not self.instance:
            if not attrs.get('patient') and not is_nouveau:
                raise serializers.ValidationError({
                    "patient": "Veuillez sélectionner un patient existant ou renseigner un nouveau patient."
                })

            if is_nouveau:
                if not attrs.get('nom') or not str(attrs.get('nom')).strip():
                    raise serializers.ValidationError({"nom": "Le nom de famille est obligatoire pour le nouveau patient."})
                if not attrs.get('prenom') or not str(attrs.get('prenom')).strip():
                    raise serializers.ValidationError({"prenom": "Le prénom est obligatoire pour le nouveau patient."})
                if not attrs.get('telephone') or not str(attrs.get('telephone')).strip():
                    raise serializers.ValidationError({"telephone": "Le numéro de téléphone est obligatoire pour créer le dossier patient."})

        date_entree = attrs.get('date_entree')
        date_sortie = attrs.get('date_sortie')
        if not date_entree and self.instance:
            date_entree = self.instance.date_entree
        if not date_sortie and self.instance:
            date_sortie = self.instance.date_sortie

        if date_entree and date_sortie and date_sortie < date_entree:
            raise serializers.ValidationError({
                "date_sortie": "La date de sortie ne peut pas être antérieure à la date d'entrée."
            })
        return attrs


class HospitalisationReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    idHospitalisation = serializers.IntegerField(source='id', read_only=True)
    id_admission = serializers.IntegerField(source='id', read_only=True)
    id_patient = serializers.IntegerField(source='patient_id', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    medecin_details = MedecinSerializer(source='medecin', read_only=True)
    lit_details = LitSerializer(source='lit', read_only=True)
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    chambre_numero = serializers.SerializerMethodField()
    lit_numero = serializers.SerializerMethodField()
    batiment_nom = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    def get_patient_nom(self, obj):
        if obj.patient and obj.patient.id_utilisateur:
            p = obj.patient.id_utilisateur
            return f"{p.prenom} {p.nom}".strip()
        return ""

    def get_medecin_nom(self, obj):
        if obj.medecin and obj.medecin.id_utilisateur:
            m = obj.medecin.id_utilisateur
            return f"Dr. {m.prenom} {m.nom}".strip()
        return "Non assigné"

    def get_chambre_numero(self, obj):
        if obj.lit and obj.lit.chambre:
            return f"Chambre {obj.lit.chambre.numero_chambre}"
        return "N/D"

    def get_lit_numero(self, obj):
        if obj.lit:
            return obj.lit.numero_lit or f"Lit #{obj.lit.id}"
        return "Non assigné"

    def get_batiment_nom(self, obj):
        if obj.lit and obj.lit.chambre and obj.lit.chambre.batiment:
            return obj.lit.chambre.batiment.nom
        return ""

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Extraire les métadonnées structurées de l'observation
        obs = instance.observation or ""
        priorite_match = re.search(r'\[Priorité\]:\s*([^\n]+)', obs)
        symptomes_match = re.search(r'\[Symptômes\]:\s*([^\n]+)', obs)
        diagnostic_match = re.search(r'\[Diagnostic provisoire\]:\s*([^\n]+)', obs)
        service_match = re.search(r'\[Service\]:\s*([^\n]+)', obs)
        antecedents_match = re.search(r'\[Antécédents\]:\s*([^\n]+)', obs)
        allergies_match = re.search(r'\[Allergies\]:\s*([^\n]+)', obs)
        traitements_match = re.search(r'\[Traitements en cours\]:\s*([^\n]+)', obs)

        ret['priorite'] = priorite_match.group(1).strip() if priorite_match else 'NORMAL'
        ret['symptomes'] = symptomes_match.group(1).strip() if symptomes_match else ''
        ret['diagnostic_provisoire'] = diagnostic_match.group(1).strip() if diagnostic_match else ''
        ret['service_nom'] = service_match.group(1).strip() if service_match else ''
        ret['antecedents'] = antecedents_match.group(1).strip() if antecedents_match else ''
        ret['allergies'] = allergies_match.group(1).strip() if allergies_match else ''
        ret['traitements_en_cours'] = traitements_match.group(1).strip() if traitements_match else ''
        return ret

    class Meta:
        model = Hospitalisation
        fields = [
            'id',
            'idHospitalisation',
            'id_admission',
            'id_patient',
            'patient',
            'patient_details',
            'medecin',
            'medecin_details',
            'lit',
            'lit_details',
            'patient_nom',
            'medecin_nom',
            'chambre_numero',
            'lit_numero',
            'batiment_nom',
            'date_entree',
            'date_sortie',
            'motif',
            'statut',
            'statut_display',
            'observation',
            'actif',
        ]
