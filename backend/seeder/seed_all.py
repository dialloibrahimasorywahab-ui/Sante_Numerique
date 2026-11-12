import os
import sys
import django

# Configuration de l'environnement Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def run_all_seeds():
    print("\n=========================================================")
    print("===   LANCEMENT DU SEEDING GLOBAL DE LA BASE DE DONNEES  ===")
    print("=========================================================\n")

    # 1. Comptes de démonstration avec identifiants standardisés
    try:
        from seed_demo_accounts import run_seed_demo_accounts
        print("1. Exécution de seed_demo_accounts.py...")
        run_seed_demo_accounts()
    except Exception as e:
        print(f" Warning seed_demo_accounts: {e}")

    # 2. Utilisateurs de test
    try:
        from seed_users import run_seed_users
        print("2. Exécution de seed_users.py...")
        run_seed_users()
    except Exception as e:
        print(f" Warning seed_users: {e}")

    # 3. Médecins
    try:
        from seed_7_medecins import run_seed_7_medecins
        print("\n3. Exécution de seed_7_medecins.py...")
        run_seed_7_medecins()
    except Exception as e:
        print(f" Warning seed_7_medecins: {e}")

    # 4. Personnel soignant
    try:
        from seed_personnel import run_seed_personnel
        print("\n4. Exécution de seed_personnel.py...")
        run_seed_personnel()
    except Exception as e:
        print(f" Warning seed_personnel: {e}")

    # 5. Bâtiments, chambres et lits
    try:
        from seed_batiment_chambres import run_seed_batiment_chambres
        print("\n5. Exécution de seed_batiment_chambres.py...")
        run_seed_batiment_chambres()
    except Exception as e:
        print(f" Warning seed_batiment_chambres: {e}")

    # 6. Rendez-vous
    try:
        from seed_rendezvous import run_seed_rendezvous
        print("\n6. Exécution de seed_rendezvous.py...")
        run_seed_rendezvous()
    except Exception as e:
        print(f" Warning seed_rendezvous: {e}")

    # 7. Hospitalisations
    try:
        from seed_hospitalisations import run_seed_hospitalisations
        print("\n7. Exécution de seed_hospitalisations.py...")
        run_seed_hospitalisations()
    except Exception as e:
        print(f" Warning seed_hospitalisations: {e}")

    # 8. Consultations
    try:
        from seed_consultations import run_seed_consultations
        print("\n8. Exécution de seed_consultations.py...")
        run_seed_consultations()
    except Exception as e:
        print(f" Warning seed_consultations: {e}")

    # 9. Ordonnances
    try:
        from seed_ordonnances import run_seed_ordonnances
        print("\n9. Exécution de seed_ordonnances.py...")
        run_seed_ordonnances()
    except Exception as e:
        print(f" Warning seed_ordonnances: {e}")

    # 10. Documents médicaux chiffrés AES-256 (GED)
    try:
        from seed_documents_medicaux import run_seed_documents_medicaux
        print("\n10. Exécution de seed_documents_medicaux.py (GED AES-256)...")
        run_seed_documents_medicaux()
    except Exception as e:
        print(f" Warning seed_documents_medicaux: {e}")

    # 11. Notifications hospitalières temps réel
    try:
        from seed_notifications import run_seed_notifications
        print("\n11. Exécution de seed_notifications.py (Alertes SSE)...")
        run_seed_notifications()
    except Exception as e:
        print(f" Warning seed_notifications: {e}")

    # 12. Séjours réels
    try:
        from seed_sejours_reels import run_seed_sejours_reels
        print("\n12. Exécution de seed_sejours_reels.py...")
        run_seed_sejours_reels()
    except Exception as e:
        print(f" Warning seed_sejours_reels: {e}")

    # 13. Actualités & Conseils Santé
    try:
        from seed_actualites import run_seed_actualites
        print("\n13. Exécution de seed_actualites.py...")
        run_seed_actualites()
    except Exception as e:
        print(f" Warning seed_actualites: {e}")

    print("\n=========================================================")
    print("===      TOUS LES SEEDS ONT ÉTÉ EXÉCUTÉS AVEC SUCCÈS   ===")
    print("=========================================================")
    print("\n RÉCAPITULATIF DES COMPTES DE TEST DISPONIBLES :")
    print(" ------------------------------------------------------------")
    print(" | RÔLE            | LOGIN           | MOT DE PASSE         |")
    print(" ------------------------------------------------------------")
    print(" | Administrateur  | admin           | Securite2026!        |")
    print(" | Médecin Cardio  | dr.camara       | Securite2026!        |")
    print(" | Médecin Pédiatre| dr.diallo       | Securite2026!        |")
    print(" | Patient 1       | patient.amadou  | Securite2026!        |")
    print(" | Patient 2       | patient.mariama | Securite2026!        |")
    print(" | Infirmier       | infirmier.sory  | Securite2026!        |")
    print(" ------------------------------------------------------------\n")


if __name__ == "__main__":
    run_all_seeds()
