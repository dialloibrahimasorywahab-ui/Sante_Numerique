import os
import random
from datetime import timedelta
from django.utils import timezone
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from patients.models import Patient
from medecin.models import Medecin
from lit.models import Lit
from hospitalisation.models import Hospitalisation
from hospitalisation.hospitalisationServices import HospitalisationService

MOTIFS_HOSPITALISATION = [
    "Crise d'appendicite aigue - Intervention chirurgicale",
    "Surveillance post-operatoire de chirurgie cardiaque",
    "Pneumonie aigue - Oxygenotherapie et traitement antibiotique",
    "Traumatologie - Fracture femur droit avec reduction",
    "Accouchement a risque et suivi neonatal",
    "Crise hypertensive majeure - Surveillance reanimation",
    "Accident Vasculaire Cerebral (AVC) - Prise en charge urgente",
    "Infection severe - Perfusion continue et observation",
    "Decompensation diabetique - Equilibrage glycemique",
    "Gastro-enterite aigue deshydratante",
]

OBSERVATIONS = [
    "Patient stable, constantes sous controle.",
    "Traitement antibiotique adminisite, bonne evolution clinique.",
    "Sortie autorisee apres bilan biologique satisfaisant.",
    "Surveillance continue de la tension et de la saturation.",
    "Repetita examens de controle prevus a H+24.",
]


def run_seed_hospitalisations():
    hosp_service = HospitalisationService()
    patients = list(Patient.objects.all())
    medecins = list(Medecin.objects.all())
    lits_dispo = list(Lit.objects.filter(etat=Lit.EtatLit.DISPONIBLE))

    if not patients or not medecins:
        print("[X] Impossible de seeder les hospitalisations: aucuns patients ou medecins trouves en base.")
        print("[!] Executez d'abord seed_users.py, seed_7_medecins.py et seed_batiment_chambres.py")
        return

    print("=========================================================")
    print("=== SEEDING DES HOSPITALISATIONS (SIMULATION) ===")
    print("=========================================================")

    now = timezone.now()
    crees = 0

    for i in range(8):
        patient = random.choice(patients)
        medecin = random.choice(medecins)
        motif = random.choice(MOTIFS_HOSPITALISATION)
        observation = random.choice(OBSERVATIONS)

        days_ago = random.randint(1, 15)
        date_entree = now - timedelta(days=days_ago, hours=random.randint(1, 12))

        # Déterminer le statut
        if i % 3 == 0 and lits_dispo:
            # Hospitalisation en cours avec lit occupé
            lit = lits_dispo.pop(0)
            statut = Hospitalisation.StatutHospitalisation.EN_COURS
            date_sortie = None
        elif i % 3 == 1 and lits_dispo:
            # Hospitalisation terminée / sortie
            lit = lits_dispo.pop(0)
            statut = Hospitalisation.StatutHospitalisation.TERMINEE
            date_sortie = date_entree + timedelta(days=random.randint(2, 7))
        else:
            # Hospitalisation programmée
            lit = None
            statut = Hospitalisation.StatutHospitalisation.PROGRAMMEE
            date_entree = now + timedelta(days=random.randint(1, 5))
            date_sortie = None

        hosp = hosp_service.admettre_patient(
            patient=patient,
            medecin=medecin,
            lit=lit,
            date_entree=date_entree,
            date_sortie=date_sortie,
            motif=motif,
            statut=statut,
            observation=observation,
        )
        crees += 1

        patient_nom = f"{patient.idUtilisateur.prenom} {patient.idUtilisateur.nom}" if patient.idUtilisateur else f"Patient #{patient.idPatient}"
        med_nom = f"Dr. {medecin.idUtilisateur.prenom} {medecin.idUtilisateur.nom}" if medecin.idUtilisateur else f"Dr. #{medecin.idMedecin}"
        lit_label = f"Lit #{lit.id} ({lit.numero_lit})" if lit else "Aucun lit"

        print(f"   |- Hosp #{hosp.id} | {patient_nom} | {med_nom} | {lit_label} | Statut: {hosp.get_statut_display()}")

    print("\n=========================================================")
    print(f" SEEDING DES HOSPITALISATIONS TERMINE ! ({crees} creees)")
    print(f" Total Hospitalisations en base : {Hospitalisation.objects.count()}")
    print("=========================================================")


if __name__ == "__main__":
    run_seed_hospitalisations()
