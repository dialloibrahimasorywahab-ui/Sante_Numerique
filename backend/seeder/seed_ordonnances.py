import os
import random
from datetime import timedelta
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from consultation.models import Consultation
from ordonnance.models import Ordonnance
from ordonnance.ordonnanceServices import OrdonnanceService

PRESCRIPTIONS_MEDICALES = [
    "Paracétamol 1000mg : 1 comprimé 3 fois par jour pendant 5 jours en cas de fièvre ou douleur.\nAmoxicilline 500mg : 1 gélule 3 fois par jour au milieu des repas pendant 7 jours.\nVitamine C 1000mg : 1 comprimé effervescent le matin pendant 10 jours.",
    "Ibuprofène 400mg : 1 comprimé 3 fois par jour au cours des repas pendant 5 jours maximum.\nOméprazole 20mg : 1 gélule le matin à jeun pendant 14 jours.\nSpasfon 80mg : 2 comprimés en cas de crise douloureuse.",
    "Amlodipine 5mg : 1 comprimé le matin au petit-déjeuner.\nLisinopril 10mg : 1 comprimé le soir au coucher.\nRégime hyposodé strict et surveillance de la tension artérielle 2 fois par semaine.",
    "Metformine 850mg : 1 comprimé 2 fois par jour au milieu des repas.\nGliclazide 60mg : 1 comprimé le matin à jeun.\nContrôle de la glycémie capillaire matin et soir.",
    "Artemether / Lumefantrine (Coartem) 80/480mg : 1 comprimé matin et soir pendant 3 jours.\nParacétamol 500mg : 2 comprimés toutes me 6 heures si fièvre supérieure à 38.5°C.\nHydratation abondante (2 à 3 litres d'eau par jour).",
    "Azithromycine 250mg : 2 comprimés le 1er jour, puis 1 comprimé par jour les 4 jours suivants.\nSirop antitussif (Hélixor) : 1 cuillère à soupe 3 fois par jour pendant 7 jours.\nLavage nasal au sérum physiologique 4 fois par jour.",
    "Sulfate ferreux + Acide folique : 1 comprimé le matin pendant 3 mois.\nVitamine D3 100.000 UI : 1 ampoule buvable par mois pendant 3 mois.\nAlimentation équilibrée riche en fer et protéines.",
    "Dextrométhorphane sirop : 1 cuillère à soupe au coucher pendant 5 jours.\nCétirizine 10mg : 1 comprimé le soir pendant 10 jours.\nInhalations de vapeur d'eau avec de l'eucalyptus 2 fois par jour.",
    "Ciprofloxacine 500mg : 1 comprimé matin et soir pendant 7 jours.\nPhloroglucinol 80mg : 2 comprimés 3 fois par jour en cas de spasmes.\nConsommer au moins 2.5 litres d'eau par jour.",
    "Diclofénac gel 1% : 1 application en massage doux sur la zone douloureuse 3 fois par jour.\nParacétamol Codeiné : 1 comprimé 3 fois par jour si douleur intense pendant 5 jours.\nRepos articulaire et application de glace 15 minutes matin et soir."
]


def run_seed_ordonnances():
    ord_service = OrdonnanceService()
    consultations = list(Consultation.objects.all())

    if not consultations:
        print("[X] Impossible de seeder les ordonnances : aucune consultation trouvée en base.")
        return

    print("=========================================================")
    print("===           SEEDING DES ORDONNANCES MEDICALES        ===")
    print("=========================================================")

    created_count = 0
    today = timezone.now().date()

    for idx, cons in enumerate(consultations, start=1):
        # Vérifier si la consultation a déjà une ordonnance
        if cons.ordonnances.exists():
            continue

        prescription = random.choice(PRESCRIPTIONS_MEDICALES)
        date_ord = cons.date_cons.date() if cons.date_cons else today

        today_str = date_ord.strftime('%Y%m%d')
        ref = f"ORD-{today_str}-{idx:03d}"

        ord_obj = ord_service.prescrire_ordonnance(
            consultation=cons,
            reference=ref,
            date_ordonnance=date_ord,
            observation=prescription
        )
        created_count += 1

        pat_name = f"{cons.patient.idUtilisateur.prenom} {cons.patient.idUtilisateur.nom}" if cons.patient and cons.patient.idUtilisateur else f"Patient #{cons.patient_id}"
        med_name = f"Dr. {cons.medecin.idUtilisateur.prenom} {cons.medecin.idUtilisateur.nom}" if cons.medecin and cons.medecin.idUtilisateur else f"Médecin #{cons.medecin_id}"

        print(f"   |- Ordonnance {ord_obj.reference} | Consultation #{cons.id} | {pat_name} | {med_name}")

    print("\n=========================================================")
    print(f" SEEDING DES ORDONNANCES TERMINE ! ({created_count} nouvelles créées)")
    print(f" Total Ordonnances en base : {Ordonnance.objects.count()}")
    print("=========================================================")


run_seed = run_seed_ordonnances

if __name__ == "__main__":
    run_seed_ordonnances()
