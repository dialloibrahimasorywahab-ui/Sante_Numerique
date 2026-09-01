import os
import random
from datetime import date, timedelta, time
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from patients.models import Patient
from medecin.models import Medecin
from rendezvous.models import RendezVous
from rendezvous.rendezvousServices import RendezVousService


MOTIFS = [
    "Consultation de routine",
    "Suivi tension artérielle",
    "Examen cardiologique annuel",
    "Soins pédiatriques",
    "Consultation gynécologique",
    "Bilan biologique et sanguin",
    "Suivi post-opératoire",
    "Douleurs thoraciques légères",
    "Contrôle glycémie et diabète",
    "Consultation dermatologique",
]

STATUTS = [
    RendezVous.StatutRendezVous.PROGRAMME,
    RendezVous.StatutRendezVous.CONFIRME,
    RendezVous.StatutRendezVous.EN_ATTENTE,
    RendezVous.StatutRendezVous.EN_COURS,
    RendezVous.StatutRendezVous.TERMINE,
    RendezVous.StatutRendezVous.ANNULE,
]


def run_seed_rendezvous():
    rdv_service = RendezVousService()
    patients = list(Patient.objects.all())
    medecins = list(Medecin.objects.all())

    if not patients or not medecins:
        print("❌ Impossible de seeder les rendez-vous: aucun patient ou médecin trouvé en base.")
        return

    print("=========================================================")
    print("=== SEEDING DES RENDEZ-VOUS (SIMULATION) ===")
    print("=========================================================")

    today = date.today()
    heures_possibles = [time(8, 30), time(9, 0), time(10, 15), time(11, 30), time(14, 0), time(15, 30), time(16, 45)]

    crees = 0
    for i in range(12):
        pat = random.choice(patients)
        med = random.choice(medecins)
        day_offset = random.randint(-5, 10)
        date_rdv = today + timedelta(days=day_offset)
        heure_rdv = random.choice(heures_possibles)
        motif_choice = random.choice(MOTIFS)
        statut_choice = random.choice(STATUTS)

        rdv = rdv_service.create_rendezvous(
            patient=pat,
            medecin=med,
            date_rdv=date_rdv,
            heure=heure_rdv,
            motif=motif_choice,
            statut=statut_choice
        )
        crees += 1
        pat_nom = f"{pat.idUtilisateur.prenom} {pat.idUtilisateur.nom}" if pat.idUtilisateur else f"Patient #{pat.idPatient}"
        med_nom = f"Dr. {med.idUtilisateur.prenom} {med.idUtilisateur.nom}" if med.idUtilisateur else f"Médecin #{med.idMedecin}"
        print(f"   |- RDV #{rdv.id} | {pat_nom} -> {med_nom} | Date: {date_rdv} {heure_rdv} | Statut: {rdv.get_statut_display()}")

    print("\n=========================================================")
    print(f" SEEDING DES RENDEZ-VOUS TERMINE ! ({crees} créés)")
    print(f" Total Rendez-vous en base : {RendezVous.objects.count()}")
    print("=========================================================")


if __name__ == "__main__":
    run_seed_rendezvous()
