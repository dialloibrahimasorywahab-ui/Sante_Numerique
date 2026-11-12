import os
import random
import secrets
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


def _generer_mot_de_passe_securise() -> str:
    """
    CORRECTION PROBLÈME 4 : Génère un mot de passe aléatoire unique par compte.
    Suppression du mot de passe fixe partagé 'MedecinPass2026!' qui constituait
    un risque de sécurité critique (credential stuffing / compromission de masse).

    Le mot de passe est généré avec secrets.token_urlsafe (cryptographiquement sûr)
    et n'est jamais affiché dans les logs ni stocké en clair.

    AVERTISSEMENT OPÉRATIONNEL :
    Si 'MedecinPass2026!' a été utilisé dans un environnement de production réel,
    les comptes concernés doivent être réinitialisés manuellement via la procédure
    d'administration sécurisée. Ne pas réutiliser ce seeder sur une base de production
    sans avoir d'abord révoqué et réinitialisé tous les accès compromis.
    """
    # Mot de passe depuis la variable d'environnement si elle est définie (ex: pipeline CI)
    env_pwd = os.environ.get("MEDECIN_SEED_PASSWORD")
    if env_pwd:
        return env_pwd

    # Sinon, génère un mot de passe aléatoire fort unique par compte
    return secrets.token_urlsafe(16)


def add_7_medecins():
    user_service = UserService()
    medecin_service = MedecinService()

    print("=== Création de 7 nouveaux médecins ===")
    print(
        "[SÉCURITÉ] Les mots de passe sont générés de façon aléatoire et unique par compte.\n"
        "           Utilisez la procédure de réinitialisation de mot de passe pour communiquer\n"
        "           les accès aux praticiens de manière sécurisée (hors de ce script)."
    )

    for i, data in enumerate(MEDECINS_DATA, start=1):
        login = f"dr_{data['prenom'].lower()}_{data['nom'].lower()}_{i+100}"
        email = f"{login}@hopital-sante.com"
        telephone = f"+22462{random.randint(1000000, 9999999)}"
        numero_ordre = f"CNOM-{random.randint(80000, 89999)}"

        # CORRECTION PROBLÈME 4 : Mot de passe aléatoire unique — jamais affiché dans les logs
        mot_de_passe = _generer_mot_de_passe_securise()

        # 1. Vérification / Création de l'utilisateur avec rôle MEDECIN
        user = User.objects.filter(login=login).first()
        if not user:
            user = user_service.createUser(
                nom=data["nom"],
                prenom=data["prenom"],
                email=email,
                telephone=telephone,
                login=login,
                motDePasseHash=mot_de_passe,
                role=User.Role.MEDECIN,
                actif=True,
            )

        del mot_de_passe

        # 2. Vérification / Création du profil Médecin rattaché à l'utilisateur
        medecin = Medecin.objects.filter(id_utilisateur=user).first()
        if not medecin:
            medecin = medecin_service.createMedecin(
                idUtilisateur=user,
                specialite=data["specialite"],
                numeroOrdre=numero_ordre,
                telephonePro=telephone,
                emailPro=email,
                bureau=data["bureau"],
                dateEmbauche="2025-01-10",
            )

        # NOTE : le login et le numéro d'ordre sont affichés, mais PAS le mot de passe
        print(
            f"[{i}/7] Succès : Dr. {user.prenom} {user.nom} "
            f"| Spécialité: {medecin.get_specialite_display()} "
            f"| N° Ordre: {medecin.numeroOrdre} | Login: {user.login}"
        )

    print("\n[OK] Les 7 médecins ont été enregistrés avec succès !")
    print(
        "[ACTION REQUISE] Communiquez les accès initiaux aux médecins via un canal sécurisé "
        "(email chiffré, SMS de réinitialisation, etc.), pas via ce script."
    )


run_seed_7_medecins = add_7_medecins


if __name__ == "__main__":
    add_7_medecins()
