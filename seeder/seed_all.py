import os
import random
from datetime import date, timedelta
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from personnel.models import Personnel
from services.models import Service
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit
from rendezvous.models import RendezVous
from hospitalisation.models import Hospitalisation
from frais_consultation.models import FraisConsultation
from consultation.models import Consultation
from ordonnance.models import Ordonnance
from natalite.models import Natalite
from natalite.nataliteServices import NataliteService
from mortalite.models import Mortalite
from mortalite.mortaliteServices import MortaliteService


def run_seed_natalite_mortalite():
    print("\n8. Seeding Natalité et Mortalité...")
    natalite_service = NataliteService()
    mortalite_service = MortaliteService()

    female_patients = list(Patient.objects.filter(sexe=Patient.Sexe.FEMININ))
    all_patients = list(Patient.objects.all())
    medecins = list(Medecin.objects.all())

    if not all_patients or not medecins:
        print("   [!] Pas assez de données pour natalité/mortalité.")
        return

    # Seed Natalité (5 naissances)
    prenoms_bebes = ["Fatoumata", "Ibrahima", "Aissatou", "Mamadou", "Mariama", "Ousmane"]
    for i in range(5):
        mere = random.choice(female_patients) if female_patients else random.choice(all_patients)
        med = random.choice(medecins)
        sexe_bebe = "F" if i % 2 == 0 else "M"
        prenom_b = prenoms_bebes[i % len(prenoms_bebes)]
        date_n = date.today() - timedelta(days=random.randint(1, 60))

        nat = natalite_service.create_nouveaune(
            id_patient=mere,
            id_medecin=med,
            nom_nouveau_ne=mere.idUtilisateur.nom if mere.idUtilisateur else "Bébé",
            prenom_nouveau_ne=prenom_b,
            date_naissance=date_n,
            heure_naissance=f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
            sexe=sexe_bebe,
            poids=round(random.uniform(2.5, 4.2), 2),
            taille=round(random.uniform(46.0, 53.0), 1),
            lieu_naissance="Maternité Principale",
            observation="Accouchement par voie basse sans complication."
        )
        print(f"   |- Naissance #{nat.pk} : {nat.prenom_nouveau_ne} {nat.nom_nouveau_ne} ({nat.sexe}, {nat.poids} kg)")

    # Seed Mortalité (3 déclarations)
    causes = ["Arrêt cardio-respiratoire", "Choc septique sévère", "Complications post-opératoires"]
    for i in range(3):
        patient = random.choice(all_patients)
        med = random.choice(medecins)
        date_d = date.today() - timedelta(days=random.randint(5, 45))

        m = mortalite_service.create_deces(
            id_patient=patient,
            id_medecin=med,
            date_deces=date_d,
            heure_deces=f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
            cause_deces=causes[i % len(causes)],
            lieu_deces="Service de Réanimation",
            observation="Constat de décès dressé par le médecin légiste / traitant."
        )
        print(f"   |- Décès #{m.pk} : Patient #{patient.idPatient} - Cause : {m.cause_deces}")


def run_all_seeds():
    print("\n" + "=" * 65)
    print("===   LANCEMENT DU SEEDING GLOBAL DE LA BASE DE DONNEES  ===")
    print("=" * 65 + "\n")

    print("0. Application des migrations de base de donnees...")
    call_command("migrate", interactive=False)
    print("   [OK] Migrations a jour.")

    try:
        from seed_users import generate_users
        print("\n1. Execution de seed_users.py (Utilisateurs, Patients, Medecins)...")
        generate_users(30)
    except Exception as e:
        print(f"   [!] Warning seed_users: {e}")

    try:
        from seed_7_medecins import add_7_medecins
        print("\n2. Execution de seed_7_medecins.py (Specialistes & Cabinets)...")
        add_7_medecins()
    except Exception as e:
        print(f"   [!] Warning seed_7_medecins: {e}")

    try:
        from seed_personnel import register_medical_staff
        print("\n3. Execution de seed_personnel.py (Services & Personnel)...")
        register_medical_staff()
    except Exception as e:
        print(f"   [!] Warning seed_personnel: {e}")

    try:
        from seed_batiment_chambres import run_seed
        print("\n4. Execution de seed_batiment_chambres.py (Batiments, Chambres & Lits)...")
        run_seed()
    except Exception as e:
        print(f"   [!] Warning seed_batiment_chambres: {e}")

    try:
        from seed_rendezvous import run_seed_rendezvous
        print("\n5. Execution de seed_rendezvous.py (Planning des RDV)...")
        run_seed_rendezvous()
    except Exception as e:
        print(f"   [!] Warning seed_rendezvous: {e}")

    try:
        from seed_hospitalisations import run_seed_hospitalisations
        print("\n6. Execution de seed_hospitalisations.py (Admissions & Sorties)...")
        run_seed_hospitalisations()
    except Exception as e:
        print(f"   [!] Warning seed_hospitalisations: {e}")

    try:
        from seed_consultations import run_seed_consultations
        print("\n7. Execution de seed_consultations.py (Frais, Consultations & Ordonnances)...")
        run_seed_consultations()
    except Exception as e:
        print(f"   [!] Warning seed_consultations: {e}")

    try:
        run_seed_natalite_mortalite()
    except Exception as e:
        print(f"   [!] Warning natalite/mortalite: {e}")

    print("\n" + "=" * 65)
    print("===      RECAPITULATIF DE LA BASE DE DONNEES INITIALISEE     ===")
    print("=" * 65)
    print(f"  • Utilisateurs       : {User.objects.count()}")
    print(f"  • Patients           : {Patient.objects.count()}")
    print(f"  • Médecins           : {Medecin.objects.count()}")
    print(f"  • Personnel Médical  : {Personnel.objects.count()}")
    print(f"  • Services           : {Service.objects.count()}")
    print(f"  • Bâtiments          : {Batiment.objects.count()}")
    print(f"  • Chambres           : {Chambre.objects.count()}")
    print(f"  • Lits               : {Lit.objects.count()} (Dispo: {Lit.objects.filter(etat=Lit.EtatLit.DISPONIBLE).count()}, Occupés: {Lit.objects.filter(etat=Lit.EtatLit.OCCUPE).count()})")
    print(f"  • Rendez-vous        : {RendezVous.objects.count()}")
    print(f"  • Hospitalisations   : {Hospitalisation.objects.count()}")
    print(f"  • Consultations      : {Consultation.objects.count()}")
    print(f"  • Frais Consultation : {FraisConsultation.objects.count()}")
    print(f"  • Ordonnances        : {Ordonnance.objects.count()}")
    print(f"  • Naissances         : {Natalite.objects.count()}")
    print(f"  • Décès              : {Mortalite.objects.count()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_all_seeds()
