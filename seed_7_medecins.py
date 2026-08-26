import os
import random
import django

# Initialisation du contexte Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User
from users.usersServices import UserService
from medecin.models import Medecin
from medecin.medecinServices import MedecinService


# Données de test pour les 7 médecins
MEDECINS_DATA = [
    {
        "nom": "Sow",
        "prenom": "Ibrahima",
        "specialite": Medecin.Specialite.CARDIOLOGIE,
        "bureau": "Cabinet 101",
    },
    {
        "nom": "Camara",
        "prenom": "Aissatou",
        "specialite": Medecin.Specialite.PEDIATRIE,
        "bureau": "Cabinet 102",
    },
    {
        "nom": "Diallo",
        "prenom": "Ousmane",
        "specialite": Medecin.Specialite.NEUROLOGIE,
        "bureau": "Cabinet 103",
    },
    {
        "nom": "Bah",
        "prenom": "Fatoumata",
        "specialite": Medecin.Specialite.GYNECOLOGIE,
        "bureau": "Cabinet 201",
    },
    {
        "nom": "Barry",
        "prenom": "Boubacar",
        "specialite": Medecin.Specialite.CHIRURGIE,
        "bureau": "Bloc Opératoire 2",
    },
    {
        "nom": "Keita",
        "prenom": "Kadiatou",
        "specialite": Medecin.Specialite.DERMATOLOGIE,
        "bureau": "Cabinet 203",
    },
    {
        "nom": "Touré",
        "prenom": "Alpha",
        "specialite": Medecin.Specialite.GENERALISTE,
        "bureau": "Cabinet 301",
    },
]


def add_7_medecins():
    user_service = UserService()
    medecin_service = MedecinService()

    print("=== Création de 7 nouveaux médecins ===")

    for i, data in enumerate(MEDECINS_DATA, start=1):
        login = f"dr_{data['prenom'].lower()}_{data['nom'].lower()}_{i+100}"
        email = f"{login}@hopital-sante.com"
        telephone = f"+22462{random.randint(1000000, 9999999)}"
        numero_ordre = f"CNOM-{random.randint(80000, 89999)}"

        # 1. Création de l'utilisateur avec rôle MEDECIN et mot de passe haché
        user = user_service.createUser(
            nom=data["nom"],
            prenom=data["prenom"],
            email=email,
            telephone=telephone,
            login=login,
            motDePasseHash="MedecinPass2026!",
            role=User.Role.MEDECIN,
            actif=True,
        )

        # 2. Création du profil Médecin rattaché à l'utilisateur
        medecin = medecin_service.createMedecin(
            idUtilisateur=user,
            specialite=data["specialite"],
            numeroOrdre=numero_ordre,
            telephonePro=telephone,
            emailPro=email,
            bureau=data["bureau"],
            dateEmbauche="2025-01-10",
        )

        print(
            f"[{i}/7] Succès : Dr. {user.prenom} {user.nom} "
            f"| Spécialité: {medecin.get_specialite_display()} "
            f"| N° Ordre: {medecin.numeroOrdre} | Login: {user.login}"
        )

    print("\n[OK] Les 7 médecins ont été enregistrés avec succès !")


run_seed_7_medecins = add_7_medecins


if __name__ == "__main__":
    add_7_medecins()
