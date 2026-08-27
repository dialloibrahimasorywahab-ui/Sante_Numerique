import os
import random
from datetime import timedelta
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from patients.models import Patient
from medecin.models import Medecin
from rendezvous.models import RendezVous
from frais_consultation.models import FraisConsultation
from frais_consultation.fraisServices import FraisConsultationService
from consultation.models import Consultation
from consultation.consultationServices import ConsultationService
from ordonnance.models import Ordonnance
from ordonnance.ordonnanceServices import OrdonnanceService

SYMPTOMES_LIST = [
    "Fievre elevee, cephalie et douleurs musculaires",
    "Toux seche persistante et maux de gorge",
    "Hypertension arterielle et vertiges",
    "Douleurs abdominales intenses et nausees",
    "Asthenie marquee et perte d'appetit",
]

DIAGNOSTICS_LIST = [
    "Syndrome grippal severe",
    "Bronchite aigue bacterienne",
    "Poussee hypertensive moderee",
    "Gastro-enterite aigue",
    "Anemie ferriprive et fatique chronique",
]

PRESCRIPTIONS_LIST = [
    "Paracetamol 1g: 1 cp 3x/jour (5 jours)\nAmoxicilline 500mg: 1 gélule 3x/jour (7 jours)\nVitamine C 1000mg: 1 cp/jour",
    "Sirop antitussif: 1 cuillere a soupe 3x/jour\nIbuprofene 400mg: 1 cp si douleur",
    "Amlodipine 5mg: 1 cp le matin\nRégime hyposodé et controle tensionnel hebdomadaire",
    "Spasfon 80mg: 2 cp 3x/jour\nSolute de rehydratation orale (SRO)",
    "Sulfate ferreux 80mg: 1 cp/jour pendant 3 mois\nApports nutritionnels enrichis",
]


def run_seed_consultations():
    frais_service = FraisConsultationService()
    cons_service = ConsultationService()
    ord_service = OrdonnanceService()

    patients = list(Patient.objects.all())
    medecins = list(Medecin.objects.all())
    rdvs = list(RendezVous.objects.all())

    if not patients or not medecins:
        print("[X] Impossible de seeder les consultations: aucun patient ou medecin trouve.")
        return

    print("=========================================================")
    print("=== SEEDING CONSULTATIONS, FRAIS & ORDONNANCES ===")
    print("=========================================================")

    now = timezone.now()
    tarifs = [5000.0, 10000.0, 15000.0, 20000.0]

    for i in range(10):
        if rdvs and i % 2 == 0:
            rdv = random.choice(rdvs)
            patient = rdv.patient
            medecin = rdv.medecin
        else:
            rdv = None
            patient = random.choice(patients)
            medecin = random.choice(medecins)
        montant = random.choice(tarifs)

        # 1. Créer le frais de consultation
        frais = frais_service.creer_frais(
            montant=montant,
            description=f"Acte de consultation medicale - {medecin.get_specialite_display() if hasattr(medecin, 'get_specialite_display') else 'Generaliste'}",
            statut=FraisConsultation.StatutPaiement.PAYE if i % 2 == 0 else FraisConsultation.StatutPaiement.EN_ATTENTE
        )

        # 2. Créer la consultation
        days_ago = random.randint(0, 10)
        date_cons = now - timedelta(days=days_ago, hours=random.randint(1, 8))

        idx = random.randint(0, len(SYMPTOMES_LIST) - 1)
        cons = cons_service.creer_consultation(
            patient=patient,
            medecin=medecin,
            rdv=rdv,
            frais=frais,
            date_cons=date_cons,
            symptomes=SYMPTOMES_LIST[idx],
            diagnostic=DIAGNOSTICS_LIST[idx],
            observations="Reconvoquer le patient si persistance des symptomes."
        )

        # 3. Créer une ordonnance pour 70% des consultations
        ord_info = ""
        if i % 10 < 7:
            prescription = PRESCRIPTIONS_LIST[idx]
            ord_obj = ord_service.prescrire_ordonnance(
                consultation=cons,
                date_ordonnance=date_cons.date(),
                observation=prescription
            )
            ord_info = f" | Ordonnance {ord_obj.reference}"

        pat_nom = f"{patient.idUtilisateur.prenom} {patient.idUtilisateur.nom}" if patient.idUtilisateur else f"Patient #{patient.idPatient}"
        med_nom = f"Dr. {medecin.idUtilisateur.prenom} {medecin.idUtilisateur.nom}" if medecin.idUtilisateur else f"Dr. #{medecin.idMedecin}"

        print(f"   |- Cons #{cons.id} | {pat_nom} | {med_nom} | Frais #{frais.id} ({frais.montant} FCFA, {frais.get_statut_display()}){ord_info}")

    print("\n=========================================================")
    print(f" SEEDING DES CONSULTATIONS TERMINE !")
    print(f" Total Frais en base         : {FraisConsultation.objects.count()}")
    print(f" Total Consultations en base : {Consultation.objects.count()}")
    print(f" Total Ordonnances en base   : {Ordonnance.objects.count()}")
    print("=========================================================")


if __name__ == "__main__":
    run_seed_consultations()
