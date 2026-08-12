from .patientRepositories import PatientRepository

class PatientService:

    # instanciation du repository pour avoir accès aux informations du repository
    def __init__(self):
        self.repository = PatientRepository()
    
    # enregistrement d'un patient
    def createPatient(self, **data):
        return self.repository.createPatient(**data)
    
    # rechercher et afficher un patient par son id
    def get_Patient(self,patient_id):
        return self.repository.get_patient(patient_id)
    
    # recuperer tous les patients et les affichers
    def get_all_patient(self):
        return self.repository.get_all_patient()

    # mettre à jour les données d'un patient
    def update_patient(self, patient, **data):
        return self.repository.update_Patient(patient, data)

    # desactiver ou archiver un patient
    def delete_patient(self,patient):
        return self.repository.delete_patient(patient)