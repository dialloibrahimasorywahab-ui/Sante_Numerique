import os
import sys
import django
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from sejour.models import Sejour, DemandeAnalyse
from sejour.sejourServices import SejourService
from mouvement.mouvementServices import MouvementService
from evenement.evenementServices import EvenementService
from patients.models import Patient
from medecin.models import Medecin
from services.models import Service
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit
from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    print("=== DÉBUT DU PEUPLEMENT DES SÉJOURS & PARCOURS PATIENTS RÉELS ===")
    
    admin_user = User.objects.filter(role__icontains='ADMIN').first()
    patients = list(Patient.objects.all()[:15])
    medecins = list(Medecin.objects.all())
    services = list(Service.objects.all())
    lits_dispos = list(Lit.objects.filter(etat="DISPONIBLE").select_related('chambre', 'chambre__batiment'))

    if not patients:
        print("Erreur : Aucun patient dans la base.")
        return
    if not medecins:
        print("Erreur : Aucun médecin dans la base.")
        return
    if not services:
        print("Erreur : Aucun service dans la base.")
        return

    sejour_service = SejourService()
    mouvement_service = MouvementService()
    evenement_service = EvenementService()

    # Définition de 8 cas de séjours réalistes
    scenarios = [
        {
            "service_search": "urgenc",
            "type": Sejour.TypePriseEnCharge.URGENCE,
            "motif": "Douleurs thoraciques aiguës et dyspnée au repos",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 6,
        },
        {
            "service_search": "urgenc",
            "type": Sejour.TypePriseEnCharge.URGENCE,
            "motif": "Traumatisme crânien léger suite à une chute",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 3,
        },
        {
            "service_search": "cardio",
            "type": Sejour.TypePriseEnCharge.HOSPITALISATION_PROGRAMMEE,
            "motif": "Surveillance post-coronarographie et bilan rythmique",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 24,
        },
        {
            "service_search": "chirurg",
            "type": Sejour.TypePriseEnCharge.HOSPITALISATION_PROGRAMMEE,
            "motif": "Intervention chirurgicale programmée - Appendicectomie",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 18,
        },
        {
            "service_search": "matern",
            "type": Sejour.TypePriseEnCharge.HOSPITALISATION_PROGRAMMEE,
            "motif": "Suivi de grossesse à risque et monitoring foetal",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 12,
        },
        {
            "service_search": "pediatr",
            "type": Sejour.TypePriseEnCharge.URGENCE,
            "motif": "Syndrome fébrile prolongé et déshydratation modérée",
            "statut": Sejour.StatutSejour.EN_COURS,
            "assign_bed": True,
            "hours_ago": 8,
        },
        {
            "service_search": "medecin",
            "type": Sejour.TypePriseEnCharge.CONSULTATION,
            "motif": "Bilan d'altération de l'état général et anémie",
            "statut": Sejour.StatutSejour.SORTIE_AUTORISEE,
            "assign_bed": True,
            "hours_ago": 48,
        },
        {
            "service_search": "neurol",
            "type": Sejour.TypePriseEnCharge.HOSPITALISATION_PROGRAMMEE,
            "motif": "Exploration de céphalées chroniques et IRM cérébrale",
            "statut": Sejour.StatutSejour.TERMINE,
            "assign_bed": False,
            "hours_ago": 72,
        },
    ]

    sejours_crees = []
    lit_idx = 0

    for idx, sc in enumerate(scenarios):
        if idx >= len(patients):
            break
        pat = patients[idx]
        med = medecins[idx % len(medecins)]
        
        # Trouver un service correspondant
        srv = next((s for s in services if sc["service_search"] in s.nom_service.lower()), services[0])
        admission_time = timezone.now() - datetime.timedelta(hours=sc["hours_ago"])

        lit = None
        chambre = None
        batiment = None
        if sc["assign_bed"] and lit_idx < len(lits_dispos):
            lit = lits_dispos[lit_idx]
            lit_idx += 1
            chambre = lit.chambre
            batiment = chambre.batiment

        data_adm = {
            "patient": pat.pk,
            "service_responsable": srv.id_service,
            "medecin_responsable": med.pk,
            "batiment": batiment.pk if batiment else None,
            "chambre": chambre.pk if chambre else None,
            "lit": lit.pk if lit else None,
            "type_prise_en_charge": sc["type"],
            "motif_admission": sc["motif"],
            "date_admission": admission_time,
            "statut": sc["statut"] if sc["statut"] != Sejour.StatutSejour.TERMINE else Sejour.StatutSejour.EN_COURS,
        }

        try:
            sejour = sejour_service.admettre_patient(data_adm, user=admin_user)
            sejours_crees.append(sejour)
            print(f"-> Séjour créé : {sejour.reference} | Patient: {pat} | Service: {srv.nom_service} | Lit: {lit}")

            # Ajouter des événements cliniques
            evenement_service.enregistrer_evenement({
                "sejour": sejour.id_sejour,
                "type_evenement": "CONSULTATION",
                "titre": "Examen clinique d'admission",
                "description": f"Constantes : TA 120/80, Pouls 75 bpm. Patient conscient et coopérant.",
                "importance": "INFO",
                "date_evenement": admission_time + datetime.timedelta(minutes=30),
            }, user=admin_user)

            # Prescription d'analyse pour les urgences/cardio
            if sc["type"] == Sejour.TypePriseEnCharge.URGENCE:
                DemandeAnalyse.objects.create(
                    patient=pat,
                    sejour=sejour,
                    prescripteur=med,
                    type_analyse="NFS, Ionogramme, Troponine ultrasensible, Gaz du sang",
                    statut=DemandeAnalyse.StatutAnalyse.EN_COURS,
                    commentaire="Résultats attendus en urgence sous 1 heure.",
                )
                evenement_service.enregistrer_evenement({
                    "sejour": sejour.id_sejour,
                    "type_evenement": "PRESCRIPTION_EXAMEN",
                    "titre": "Bilan biologique d'urgence prescrit",
                    "description": "NFS, Ionogramme et marqueurs cardiaques envoyés au laboratoire.",
                    "importance": "ATTENTION",
                    "date_evenement": admission_time + datetime.timedelta(minutes=45),
                }, user=admin_user)

        except Exception as e:
            print(f"Erreur admission patient {pat}: {e}")

    # Réaliser un transfert pour l'un des séjours actifs
    if len(sejours_crees) >= 2 and lit_idx < len(lits_dispos):
        sejour_transfert = sejours_crees[0]
        nouveau_lit = lits_dispos[lit_idx]
        lit_idx += 1
        nouveau_srv = next((s for s in services if "cardio" in s.nom_service.lower()), services[1])
        
        print(f"\n-> Enregistrement d'un transfert pour {sejour_transfert.reference} vers Lit #{nouveau_lit.numero_lit}...")
        try:
            mouvement_service.enregistrer_transfert({
                "sejour": sejour_transfert.id_sejour,
                "service_destination": nouveau_srv.id_service,
                "batiment_destination": nouveau_lit.chambre.batiment.pk,
                "chambre_destination": nouveau_lit.chambre.pk,
                "lit_destination": nouveau_lit.pk,
                "type_mouvement": "TRANSFERT_SERVICE",
                "motif": "Stabilisation aux urgences réussie, transfert en hospitalisation conventionnelle",
                "commentaire": "Surveillance continue requise",
                "date_mouvement": timezone.now() - datetime.timedelta(hours=1),
            }, user=admin_user)
            print("Transfert effectué avec succès.")
        except Exception as e:
            print(f"Erreur transfert: {e}")

    # Clôturer le dernier séjour pour avoir une sortie réelle
    if len(sejours_crees) >= 8:
        sejour_sortie = sejours_crees[-1]
        try:
            sejour_service.autoriser_sortie(sejour_sortie.id_sejour, motif="Amélioration clinique complète, retour à domicile")
            sejour_service.cloturer_sejour(sejour_sortie.id_sejour, {
                "motif_sortie": "Retour à domicile avec traitement ambulatoire",
                "commentaire": "Ordonnance remise, consultation de suivi dans 15 jours",
                "date_sortie": timezone.now() - datetime.timedelta(hours=2),
            }, user=admin_user)
            print(f"\n-> Sortie définitive enregistrée pour {sejour_sortie.reference}.")
        except Exception as e:
            print(f"Erreur clôture: {e}")

    print("\n=== PEUPLEMENT DU PARCOURS TERMINÉ AVEC SUCCÈS ===")

if __name__ == "__main__":
    run()
