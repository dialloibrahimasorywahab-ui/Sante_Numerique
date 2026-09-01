from .models import Patient


class PatientRepository:
    # enregistrement d'un patient
    def createPatient(self, **data):
        return Patient.objects.create(**data)

    # rechercher et afficher un patient
    def get_patient(self, patient_id):
        try:
            return Patient.objects.select_related('id_utilisateur').get(pk=patient_id)
        except Patient.DoesNotExist:
            return None

    # afficher tous les patients
    def get_all_patient(self, actif_only: bool = True):
        qs = Patient.objects.select_related('id_utilisateur').all()
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    # rechercher des patients par nom, prénom, email, téléphone ou n° sécu
    def search_patients(self, query, actif_only: bool = True):
        if not query:
            return self.get_all_patient(actif_only=actif_only)
        from django.db.models import Q
        clean_q = str(query).strip()
        qs = Patient.objects.filter(
            Q(id_utilisateur__nom__icontains=clean_q) |
            Q(id_utilisateur__prenom__icontains=clean_q) |
            Q(id_utilisateur__email__icontains=clean_q) |
            Q(id_utilisateur__telephone__icontains=clean_q) |
            Q(numero_securite_sociale__icontains=clean_q)
        ).select_related('id_utilisateur')
        if actif_only:
            qs = qs.filter(id_utilisateur__actif=True)
        return qs

    # mettre à jour les informations d'un patient
    def update_Patient(self, patient, **data):
        for field, value in data.items():
            setattr(patient, field, value)
        patient.save()
        return patient

    # desactiver (soft delete) ou supprimer un patient
    def delete_patient(self, patient, hard=False):
        if hard:
            user = patient.id_utilisateur
            patient.delete()
            if user:
                user.delete()
            return True

        if patient.id_utilisateur:
            patient.id_utilisateur.actif = False
            patient.id_utilisateur.save(update_fields=["actif"])
        return True