from django.utils import timezone
from users.models import User
from patients.models import Patient


def creer_test_utilisateur(login: str, role: str = "ADMINISTRATEUR", email: str = None) -> User:
    return User.objects.create_user(
        login=login,
        email=email or f"{login}@hopital.test",
        password="Password123!",
        nom=login.replace("_", " ").title(),
        prenom="Agent",
        telephone=f"620{abs(hash(login)) % 1000000:06d}",
        role=role,
    )


def creer_test_patient(login: str = "patient_test") -> Patient:
    user = creer_test_utilisateur(login=login, role="PATIENT")
    return Patient.objects.create(
        id_utilisateur=user,
        date_naissance="1990-05-15",
        sexe=Patient.Sexe.FEMININ,
        adresse="Conakry",
        groupe_sanguin=Patient.GroupeSanguin.O_POSITIF,
        date_inscription=timezone.now().date(),
        numero_securite_sociale=f"NSS-{abs(hash(login)) % 1000000:06d}",
    )
