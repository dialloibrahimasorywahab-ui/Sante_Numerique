from .models import Patient


class PatientRepository:
    # enregistrement d'un patient
    def createPatient(self, **data):
        return Patient.objects.create(**data)

    # rechercher et afficher un patient
    def get_patient(self, patient_id):
        try:
            return Patient.objects.select_related('idUtilisateur').get(idPatient=patient_id)
        except Patient.DoesNotExist:
            return None

    # afficher tous les patients
    def get_all_patient(self):
        return Patient.objects.select_related('idUtilisateur').all()

    # rechercher des patients par nom, prénom, email, téléphone ou n° sécu
    def search_patients(self, query):
        if not query:
            return self.get_all_patient()
        from django.db.models import Q
        clean_q = str(query).strip()
        return Patient.objects.filter(
            Q(idUtilisateur__nom__icontains=clean_q) |
            Q(idUtilisateur__prenom__icontains=clean_q) |
            Q(idUtilisateur__email__icontains=clean_q) |
            Q(idUtilisateur__telephone__icontains=clean_q) |
            Q(numeroSecuriteSociale__icontains=clean_q)
        ).select_related('idUtilisateur')

    # mettre à jour les informations d'un patient
    def update_Patient(self, patient, **data):
        for field, value in data.items():
            setattr(patient, field, value)
        patient.save()
        return patient

    # desactiver (soft delete) ou supprimer un patient
    def delete_patient(self, patient, hard=False):
        if hard:
            user = patient.idUtilisateur
            patient.delete()
            if user:
                user.delete()
            return True

        if patient.idUtilisateur:
            patient.idUtilisateur.actif = False
            patient.idUtilisateur.save(update_fields=["actif"])
        return True