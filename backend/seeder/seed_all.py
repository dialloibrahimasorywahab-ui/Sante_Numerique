import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'seeder'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def run_all_seeds():
    print("\n=========================================================")
    print("===   LANCEMENT DU SEEDING GLOBAL DE LA BASE DE DONNEES  ===")
    print("=========================================================\n")

    try:
        from seed_users import run_seed_users
        print("1. Execution de seed_users.py...")
        run_seed_users()
    except Exception as e:
        print(f" Warning seed_users: {e}")

    try:
        from seed_7_medecins import run_seed_7_medecins
        print("\n2. Execution de seed_7_medecins.py...")
        run_seed_7_medecins()
    except Exception as e:
        print(f" Warning seed_7_medecins: {e}")

    try:
        from seed_personnel import run_seed_personnel
        print("\n3. Execution de seed_personnel.py...")
        run_seed_personnel()
    except Exception as e:
        print(f" Warning seed_personnel: {e}")

    try:
        from seed_batiment_chambres import run_seed_batiment_chambres
        print("\n4. Execution de seed_batiment_chambres.py...")
        run_seed_batiment_chambres()
    except Exception as e:
        print(f" Warning seed_batiment_chambres: {e}")

    try:
        from seed_rendezvous import run_seed_rendezvous
        print("\n5. Execution de seed_rendezvous.py...")
        run_seed_rendezvous()
    except Exception as e:
        print(f" Warning seed_rendezvous: {e}")

    try:
        from seed_hospitalisations import run_seed_hospitalisations
        print("\n6. Execution de seed_hospitalisations.py...")
        run_seed_hospitalisations()
    except Exception as e:
        print(f" Warning seed_hospitalisations: {e}")

    try:
        from seed_consultations import run_seed_consultations
        print("\n7. Execution de seed_consultations.py...")
        run_seed_consultations()
    except Exception as e:
        print(f" Warning seed_consultations: {e}")

    try:
        from seed_ordonnances import run_seed_ordonnances
        print("\n8. Execution de seed_ordonnances.py...")
        run_seed_ordonnances()
    except Exception as e:
        print(f" Warning seed_ordonnances: {e}")

    print("\n=========================================================")
    print("===      TOUS LES SEEDS ONT ETE EXECUTES AVEC SUCCES    ===")
    print("=========================================================\n")


if __name__ == "__main__":
    run_all_seeds()
