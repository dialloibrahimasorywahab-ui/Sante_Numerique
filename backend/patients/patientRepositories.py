from common.repositories import BaseRepository
from .models import Patient


class PatientRepository(BaseRepository[Patient]):
    """
    Repository pour la gestion des données des patients.
    Hérite des méthodes CRUD génériques de BaseRepository.
    """
    def __init__(self):
        super().__init__(model=Patient)

    def createPatient(self, **data):
        return self.create(**data)

    def get_patient(self, patient_id):
        return self.get_by_id(patient_id, select_related=['id_utilisateur'])

    def get_all_patient(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only, select_related=['id_utilisateur'])

    def search_patients(self, query, actif_only: bool = True):
        return self.search(
            query=query,
            search_fields=[
                'id_utilisateur__nom',
                'id_utilisateur__prenom',
                'id_utilisateur__email',
                'id_utilisateur__telephone',
                'numero_securite_sociale'
            ],
            actif_only=actif_only,
            select_related=['id_utilisateur']
        )

    def update_Patient(self, patient, **data):
        return self.update(patient, **data)

    def delete_patient(self, patient, hard=False):
        return self.delete(patient, hard=hard)