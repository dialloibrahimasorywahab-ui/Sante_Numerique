from .models import Patient


class PatientRepository:
    # enregistrement d'un patient
    def createPatient(self, **data):
        return Patient.objects.create(**data)

    # rechercher et afficher un patient
    def get_patient(self, patient_id):
        try:
            return Patient.objects.get(idPatient=patient_id)
        except Patient.DoesNotExist:
            return None

    # afficher tous les patients
    def get_all_patient(self):
        return Patient.objects.all()

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