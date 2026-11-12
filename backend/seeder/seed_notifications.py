import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from notifications.models import NotificationHospitaliere
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from lit.models import Lit


def run_seed_notifications():
    print("\n=========================================================")
    print("=== SEEDING DES NOTIFICATIONS HOSPITALIÈRES (TEMPS RÉEL) ===")
    print("=========================================================")

    # Récupération des entités pour enrichir les métadonnées
    patients = list(Patient.objects.select_related('id_utilisateur').all())
    medecins = list(Medecin.objects.select_related('id_utilisateur').all())
    lits = list(Lit.objects.select_related('chambre__batiment').all())

    pat1_nom = f"{patients[0].id_utilisateur.prenom} {patients[0].id_utilisateur.nom}" if patients else "Amadou Sow"
    pat2_nom = f"{patients[1].id_utilisateur.prenom} {patients[1].id_utilisateur.nom}" if len(patients) > 1 else "Mariama Barry"
    med1_nom = f"Dr. {medecins[0].id_utilisateur.prenom} {medecins[0].id_utilisateur.nom}" if medecins else "Dr. Mohamed Camara"
    lit_ref = lits[0].numero_lit if lits else "L-102"
    lit_chambre = f"Chambre {lits[0].chambre.numero_chambre}" if lits and lits[0].chambre else "Chambre 102"

    SAMPLE_NOTIFICATIONS = [
        {
            "type_notification": NotificationHospitaliere.TypeNotification.LIT_URGENCE,
            "titre": f"Urgence Vitale : Affectation immédiate Lit {lit_ref}",
            "message": f"Le lit {lit_ref} ({lit_chambre}, Pavillon Urgences & Réanimation) a été réservé en urgence pour {pat1_nom}.",
            "donnees": {
                "id_lit": lits[0].id if lits else 1,
                "numero_lit": lit_ref,
                "patient": pat1_nom,
                "priorite": "URGENT",
                "service": "Urgences & Soins Intensifs"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.TOUS,
            "lu": False,
            "delta_minutes": 5,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.PATIENT_ARRIVE,
            "titre": f"Patient arrivé en salle d'attente : {pat2_nom}",
            "message": f"{pat2_nom} est arrivée à l'accueil et installée en salle d'attente pour sa consultation avec {med1_nom}.",
            "donnees": {
                "patient": pat2_nom,
                "medecin": med1_nom,
                "salle_attente": "Salle B — Cabinet 101",
                "statut": "EN_ATTENTE"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.MEDECIN,
            "lu": False,
            "delta_minutes": 18,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.ALERTE_CLINIQUE,
            "titre": "Résultat Biologique Critique : Kaliémie à 2.7 mmol/L",
            "message": f"Alerte laboratoire automatisée : Hypokaliémie sévère détectée pour le dossier de {pat1_nom}. Ajustement thérapeutique requis.",
            "donnees": {
                "parametre": "Kaliémie (K+)",
                "valeur": "2.7 mmol/L",
                "norme": "3.5 - 5.0 mmol/L",
                "degre_gravite": "CRITIQUE"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.MEDECIN,
            "lu": False,
            "delta_minutes": 42,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.LIT_URGENCE,
            "titre": "Libération de lit : Lit Réanimation disponible",
            "message": "Le lit de réanimation R-04 a été désinfecté et validé par l'équipe soignante. Disponible pour nouvelles admissions.",
            "donnees": {
                "lit": "R-04",
                "etat": "DISPONIBLE",
                "service": "Réanimation Polyvalente"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.TOUS,
            "lu": True,
            "delta_minutes": 90,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.HOSPITALISATION,
            "titre": f"Admission validée en Cardiologie : {pat1_nom}",
            "message": f"Entrée administrative et médicale confirmée pour {pat1_nom}. Transfert prévu au 2ème étage.",
            "donnees": {
                "patient": pat1_nom,
                "service": "Cardiologie Interventionnelle",
                "mode_entree": "Urgences"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.INFIRMIER,
            "lu": True,
            "delta_minutes": 150,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.NOUVEAU_RDV,
            "titre": "Programmation prioritaire : Consultation Spécialisée",
            "message": f"Nouveau rendez-vous d'évaluation cardiologique programmé le 02/10/2026 à 10:15 avec {med1_nom}.",
            "donnees": {
                "date": "2026-10-02",
                "heure": "10:15",
                "motif": "Suivi post-infarctus"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.MEDECIN,
            "lu": True,
            "delta_minutes": 240,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.PATIENT_ARRIVE,
            "titre": f"Patient en attente : Consultation Pédiatrique",
            "message": "Un jeune patient accompagné est pris en charge en salle d'attente pédiatrique.",
            "donnees": {
                "salle_attente": "Salle Pédiatrie — Pavillon Mère-Enfant",
                "ordre": 1
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.MEDECIN,
            "lu": False,
            "delta_minutes": 12,
        },
        {
            "type_notification": NotificationHospitaliere.TypeNotification.INFO,
            "titre": "Maintenance Planifiée du Système d'Imagerie PACS",
            "message": "Une opération de mise à jour des serveurs d'imagerie médicale est planifiée cette nuit entre 02h00 et 03h00.",
            "donnees": {
                "impact": "Accès imagerie hors-ligne pendant 30 min",
                "equipe": "DSI Santé Numérique"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.TOUS,
            "lu": True,
            "delta_minutes": 600,
        }
    ]

    now = timezone.now()
    created_count = 0

    for notif_data in SAMPLE_NOTIFICATIONS:
        notif = NotificationHospitaliere.objects.create(
            type_notification=notif_data["type_notification"],
            titre=notif_data["titre"],
            message=notif_data["message"],
            donnees=notif_data["donnees"],
            destinataire_role=notif_data["destinataire_role"],
            lu=notif_data["lu"]
        )
        # Ajuster l'horodatage pour étaler l'historique
        notif.date_creation = now - timedelta(minutes=notif_data["delta_minutes"])
        notif.save(update_fields=["date_creation"])
        created_count += 1

        statut_lu = "Lue" if notif.lu else "NON LUE"
        print(f" [{created_count}/{len(SAMPLE_NOTIFICATIONS)}] Notif : [{notif.type_notification}] '{notif.titre}' | {statut_lu}")

    print(f"\n[OK] {created_count} notifications hospitalières ont été injectées avec succès !")
    print(f" Total Notifications en base : {NotificationHospitaliere.objects.count()}")
    print("=========================================================\n")


if __name__ == "__main__":
    run_seed_notifications()
