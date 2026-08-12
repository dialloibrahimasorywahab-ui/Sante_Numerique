from .models import Patient

class PatientRepository:
    # enregistrement d'un patient
    def createPatient(self, **data):
        return Patient.objects.create(**data)
    
    # rechercher et afficher un patient
    def get_patient(self, patient_id):
        return Patient.objects.get(idPatient = patient_id)

    # afficher tous les patients
    def get_all_patient(self):
        return Patient.objects.all()
    
    # mettre à jour les informations d'un patient
    def update_Patient(self, patient, **data):
        for field, value in data.items():
            setattr(patient, field.value)
        patient.save()

        return patient

    # archiver ou desactiver un compte d'un patient sans pour autant supprimer les données
    def delete_patient(self, patient):
        patient.delete()