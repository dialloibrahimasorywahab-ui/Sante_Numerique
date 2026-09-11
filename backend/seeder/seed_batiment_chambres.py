import os
import random
# pyrefly: ignore [missing-import]
import django

# Initialisation du contexte Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from batiment.batimentServices import BatimentService
from chambre.chambreServices import ChambreService
from chambre.models import Chambre
from lit.litServices import LitService
from lit.models import Lit


BATIMENTS_SEED_DATA = [
    {
        "nom": "Bâtiment Principal — Pavillon A",
        "description": "Consultations externes, Médecine Générale et Soins Polyvalents",
        "chambres": [
            {"numero_chambre": 1, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 2, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 3, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 4, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 5, "type_chambre": Chambre.TypeChambre.SUITE, "capacite": 2},
            {"numero_chambre": 6, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 7, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 8, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 9, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 10, "type_chambre": Chambre.TypeChambre.SUITE, "capacite": 2},
            {"numero_chambre": 11, "type_chambre": Chambre.TypeChambre.COMMUNE, "capacite": 4},
            {"numero_chambre": 12, "type_chambre": Chambre.TypeChambre.COMMUNE, "capacite": 6},
        ]
    },
    {
        "nom": "Pavillon des Urgences & Réanimation",
        "description": "Accueil des urgences, soins intensifs et unité de réanimation",
        "chambres": [
            {"numero_chambre": 1, "type_chambre": Chambre.TypeChambre.URGENCES, "capacite": 1},
            {"numero_chambre": 2, "type_chambre": Chambre.TypeChambre.URGENCES, "capacite": 1},
            {"numero_chambre": 3, "type_chambre": Chambre.TypeChambre.URGENCES, "capacite": 2},
            {"numero_chambre": 4, "type_chambre": Chambre.TypeChambre.URGENCES, "capacite": 2},
            {"numero_chambre": 5, "type_chambre": Chambre.TypeChambre.REANIMATION, "capacite": 1},
            {"numero_chambre": 6, "type_chambre": Chambre.TypeChambre.REANIMATION, "capacite": 1},
            {"numero_chambre": 7, "type_chambre": Chambre.TypeChambre.REANIMATION, "capacite": 1},
            {"numero_chambre": 8, "type_chambre": Chambre.TypeChambre.URGENCES, "capacite": 2},
        ]
    },
    {
        "nom": "Pôle Maternité & Gynécologie — Pavillon B",
        "description": "Services de gynécologie, obstétrique, salles d'accouchement et suites",
        "chambres": [
            {"numero_chambre": 1, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 2, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 3, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 4, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 5, "type_chambre": Chambre.TypeChambre.SUITE, "capacite": 2},
            {"numero_chambre": 6, "type_chambre": Chambre.TypeChambre.SUITE, "capacite": 2},
        ]
    },
    {
        "nom": "Bloc Opératoire & Chirurgie Centrale",
        "description": "Interventions chirurgicales et hospitalisation post-opératoire",
        "chambres": [
            {"numero_chambre": 1, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 2, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 3, "type_chambre": Chambre.TypeChambre.REANIMATION, "capacite": 1},
            {"numero_chambre": 4, "type_chambre": Chambre.TypeChambre.REANIMATION, "capacite": 1},
            {"numero_chambre": 5, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 6, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
        ]
    },
    {
        "nom": "Pavillon des Spécialités Médicales — Pavillon C",
        "description": "Cardiologie, Neurologie, Dermatologie et Radiologie",
        "chambres": [
            {"numero_chambre": 1, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 2, "type_chambre": Chambre.TypeChambre.INDIVIDUELLE, "capacite": 1},
            {"numero_chambre": 3, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 4, "type_chambre": Chambre.TypeChambre.DOUBLE, "capacite": 2},
            {"numero_chambre": 5, "type_chambre": Chambre.TypeChambre.SUITE, "capacite": 2},
            {"numero_chambre": 6, "type_chambre": Chambre.TypeChambre.COMMUNE, "capacite": 4},
        ]
    }
]


# Liste pondérée d'états de lits pour simuler une occupation réaliste
ETATS_DISTRIBUTION = [
    Lit.EtatLit.DISPONIBLE, Lit.EtatLit.DISPONIBLE, Lit.EtatLit.DISPONIBLE,
    Lit.EtatLit.OCCUPE, Lit.EtatLit.OCCUPE,
    Lit.EtatLit.RESERVE,
    Lit.EtatLit.EN_NETTOYAGE,
]


def run_seed():
    batiment_svc = BatimentService()
    chambre_svc = ChambreService()
    lit_svc = LitService()

    print("=========================================================")
    print("=== SEEDING DES BÂTIMENTS, CHAMBRES ET LITS (SIMULATION) ===")
    print("=========================================================")

    total_batiments_crees = 0
    total_chambres_creees = 0
    total_lits_traités = 0

    for bat_info in BATIMENTS_SEED_DATA:
        nom = bat_info["nom"]
        desc = bat_info["description"]
        chambres_list = bat_info["chambres"]
        nombre_requis = len(chambres_list)

        batiment = batiment_svc.get_or_create_batiment(
            nom=nom,
            nombre_chambre=nombre_requis,
            description=desc
        )
        total_batiments_crees += 1

        print(f"\n Bâtiment : {batiment.nom} (ID: {batiment.idBatiment})")

        for ch_data in chambres_list:
            num = ch_data["numero_chambre"]
            type_ch = ch_data["type_chambre"]
            cap = ch_data["capacite"]

            existing_chambres = Chambre.objects.filter(
                batiment=batiment,
                numero_chambre=num
            )
            if existing_chambres.exists():
                chambre = existing_chambres.first()
                if chambre.capacite != cap or chambre.type_chambre != type_ch:
                    chambre.capacite = cap
                    chambre.type_chambre = type_ch
                    chambre.save()
            else:
                chambre = chambre_svc.create_chambre(
                    batiment=batiment,
                    numero_chambre=num,
                    type_chambre=type_ch,
                    capacite=cap
                )
                total_chambres_creees += 1

            # Générer les lits s'ils manquent
            lit_svc.generate_lits_pour_chambre(chambre)

            # Assigner des états variés et réalistes aux lits
            lits = list(chambre.lits.all())
            for idx, lit in enumerate(lits):
                total_lits_traités += 1
                # Assigner un état varié
                nouvel_etat = random.choice(ETATS_DISTRIBUTION)
                lit_svc.update_lit(lit, etat=nouvel_etat)

            nb_lits_chambre = len(lits)
            print(f"   |- Chambre {chambre.numero_chambre} | Type: {chambre.get_type_chambre_display()} | Capacite: {chambre.capacite} | Lits: {nb_lits_chambre}")

        batiment_svc.sync_nombre_chambres(batiment.idBatiment)
        print(f"   Total chambres enregistrees : {batiment.nombre_chambre}")

    print("\n=========================================================")
    print("  SEEDING TERMINE AVEC SUCCES !")
    print(f" Total Batiments traites : {total_batiments_crees}")
    print(f" Total Chambres : {Chambre.objects.count()}")
    print(f" Total Lits en base de donnees : {Lit.objects.count()}")
    print("   - Lits Disponibles  :", Lit.objects.filter(etat=Lit.EtatLit.DISPONIBLE).count())
    print("   - Lits Occupes      :", Lit.objects.filter(etat=Lit.EtatLit.OCCUPE).count())
    print("   - Lits Reserves     :", Lit.objects.filter(etat=Lit.EtatLit.RESERVE).count())
    print("   - Lits En Nettoyage :", Lit.objects.filter(etat=Lit.EtatLit.EN_NETTOYAGE).count())
    print("=========================================================")


run_seed_batiment_chambres = run_seed


if __name__ == "__main__":
    run_seed()
