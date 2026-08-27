from django.db import transaction
from django.utils import timezone
from users.models import User
from users.usersServices import UserService
from .patientRepositories import PatientRepository


class PatientService:

    # Instanciation du repository et du service utilisateur
    def __init__(self):
        self.repository = PatientRepository()
        self.user_service = UserService()

    # Enregistrement d'un patient (prend en charge la création combinée User + Patient)
    def createPatient(self, **data):
        id_user_data = data.pop("idUtilisateur", None)

        if isinstance(id_user_data, User):
            user = id_user_data
        elif isinstance(id_user_data, dict):
            user_info = id_user_data
            login = data.pop("login", user_info.get("login", ""))
            password = data.pop("motDePasse", "DefaultPass123!")

            user_payload = {
                "nom": user_info.get("nom", ""),
                "prenom": user_info.get("prenom", ""),
                "email": user_info.get("email", ""),
                "telephone": user_info.get("telephone", ""),
                "login": login,
                "motDePasseHash": password,
                "role": User.Role.PATIENT,
                "actif": True,
            }
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)
        elif id_user_data is None and ("nom" in data or "login" in data):
            user_payload = {
                "nom": data.pop("nom", ""),
                "prenom": data.pop("prenom", ""),
                "email": data.pop("email", ""),
                "telephone": data.pop("telephone", ""),
                "login": data.pop("login", ""),
                "motDePasseHash": data.pop("motDePasse", "DefaultPass123!"),
                "role": User.Role.PATIENT,
                "actif": True,
            }
            with transaction.atomic():
                user = self.user_service.createUser(**user_payload)
        else:
            user = None

        data.pop("login", None)
        data.pop("motDePasse", None)

        if user:
            data["idUtilisateur"] = user

        if "dateInscription" not in data or not data["dateInscription"]:
            data["dateInscription"] = timezone.now().date()

        return self.repository.createPatient(**data)

    # rechercher et afficher un patient par son id
    def get_Patient(self, patient_id):
        return self.repository.get_patient(patient_id)

    # recuperer tous les patients et les affichers
    def get_all_patient(self):
        return self.repository.get_all_patient()

    # rechercher des patients
    def search_patients(self, query):
        return self.repository.search_patients(query)

    # mettre à jour les données d'un patient
    def update_patient(self, patient, **data):
        id_user_data = data.pop("idUtilisateur", None)
        user_updates = {}

        if isinstance(id_user_data, dict):
            user_updates.update(id_user_data)
        elif isinstance(id_user_data, User):
            patient.idUtilisateur = id_user_data

        for key in ["nom", "prenom", "email", "telephone", "dateNaissance", "login", "motDePasse", "motDePasseHash"]:
            if key in data:
                user_updates[key] = data.pop(key)

        data.pop("login", None)
        data.pop("motDePasse", None)

        with transaction.atomic():
            if user_updates and patient.idUtilisateur:
                self.user_service.updateUser(patient.idUtilisateur, **user_updates)
            return self.repository.update_Patient(patient, **data)

    # desactiver ou archiver un patient
    def delete_patient(self, patient, hard=False):
        return self.repository.delete_patient(patient, hard=hard)