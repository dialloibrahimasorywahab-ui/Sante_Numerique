import os
import random
import django

# Initialisation de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User
from users.usersServices import UserService
from patients.models import Patient
from patients.patientServices import PatientService
from medecin.models import Medecin
from medecin.medecinServices import MedecinService


PRENOMS_PAR_SEXE = [
    ("Amadou", Patient.Sexe.MASCULIN),
    ("Fatoumata", Patient.Sexe.FEMININ),
    ("Ibrahima", Patient.Sexe.MASCULIN),
    ("Aissatou", Patient.Sexe.FEMININ),
    ("Mamadou", Patient.Sexe.MASCULIN),
    ("Mariama", Patient.Sexe.FEMININ),
    ("Ousmane", Patient.Sexe.MASCULIN),
    ("Kadiatou", Patient.Sexe.FEMININ),
    ("Boubacar", Patient.Sexe.MASCULIN),
    ("Binta", Patient.Sexe.FEMININ),
    ("Alpha", Patient.Sexe.MASCULIN),
    ("Sainabou", Patient.Sexe.FEMININ),
    ("Mohamed", Patient.Sexe.MASCULIN),
    ("Hawa", Patient.Sexe.FEMININ),
    ("Cherif", Patient.Sexe.MASCULIN),
    ("Aminata", Patient.Sexe.FEMININ),
    ("Sory", Patient.Sexe.MASCULIN),
    ("Fanta", Patient.Sexe.FEMININ),
]

PRENOMS = [prenom for prenom, _ in PRENOMS_PAR_SEXE]

NOMS = [
    "Diallo", "Bah", "Barry", "Sow", "Camara", "Sylla",
    "Traore", "Soumah", "Keita", "Touré", "Cissé", "Kaba",
    "Conte", "Bangoura", "Kouyaté", "Mara"
]

ROLES = [
    User.Role.PATIENT,
    User.Role.ADMINISTRATEUR,
    User.Role.MEDECIN,
    User.Role.INFIRMIER,
]

SPECIALITES = [
    Medecin.Specialite.GENERALISTE,
    Medecin.Specialite.CARDIOLOGIE,
    Medecin.Specialite.PEDIATRIE,
    Medecin.Specialite.GYNECOLOGIE,
    Medecin.Specialite.NEUROLOGIE,
    Medecin.Specialite.CHIRURGIE,
]

GROUPES_SANGUINS = [
    Patient.GroupeSanguin.A_POSITIF,
    Patient.GroupeSanguin.A_NEGATIF,
    Patient.GroupeSanguin.B_POSITIF,
    Patient.GroupeSanguin.B_NEGATIF,
    Patient.GroupeSanguin.AB_POSITIF,
    Patient.GroupeSanguin.AB_NEGATIF,
    Patient.GroupeSanguin.O_POSITIF,
    Patient.GroupeSanguin.O_NEGATIF,
]

def generate_users(count=50):
    user_service = UserService()
    patient_service = PatientService()
    medecin_service = MedecinService()
    created_count = 0

    print(f"=== Début de la génération de {count} utilisateurs ===")

    for i in range(1, count + 1):
        prenom, sexe = random.choice(PRENOMS_PAR_SEXE)
        nom = random.choice(NOMS)
        login = f"{prenom.lower()}_{nom.lower()}_{i}"
        email = f"{login}@santenumerique.com"
        telephone = f"+2246{random.randint(10000000, 99999999)}"
        role = ROLES[(i - 1) % len(ROLES)]  # Distribution équilibrée des 4 rôles

        # Création de l'utilisateur avec hachage automatique du mot de passe
        user = user_service.createUser(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            login=login,
            motDePasseHash=f"PassWord_{i}!",
            role=role,
            actif=True,
        )
        created_count += 1

        # Si le rôle est PATIENT, on lui génère également un profil Patient
        if role == User.Role.PATIENT:
            patient_service.createPatient(
                idUtilisateur=user,
                dateNaissance=f"{random.randint(1965, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                sexe=sexe,
                adresse=f"{random.randint(1, 150)} Avenue de la Santé",
                groupeSanguin=random.choice(GROUPES_SANGUINS),
                numeroSecuriteSociale=f"1{random.randint(70, 99)}{random.randint(10000000, 99999999)}",
                personneAContacter=f"{random.choice(PRENOMS)} {nom}",
                dateInscription="2026-01-01",
            )
        elif role == User.Role.MEDECIN:
            medecin_service.createMedecin(
                idUtilisateur=user,
                specialite=random.choice(SPECIALITES),
                numeroOrdre=f"CNOM-{random.randint(10000, 99999)}",
                telephonePro=telephone,
                emailPro=email,
                bureau=f"Cabinet {random.randint(101, 305)}",
                dateEmbauche="2024-01-15",
            )

        print(f"[{i}/{count}] Utilisateur créé : {prenom} {nom} | Rôle: {role} | Login: {login}")

    print(f"\n[OK] {created_count} utilisateurs (et leurs fiches associées) ont ete generes avec succes !")


run_seed_users = generate_users


if __name__ == "__main__":
    generate_users(50)
