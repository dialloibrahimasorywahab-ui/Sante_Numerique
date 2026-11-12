import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from personnel.models import Personnel


DEMO_PASSWORD = "Securite2026!"


def get_or_create_resilient_user(login, email, telephone, defaults):
    user = User.objects.filter(login=login).first()
    if not user:
        user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.filter(telephone=telephone).first()

    if user:
        user.login = login
        user.email = email
        user.telephone = telephone
        for k, v in defaults.items():
            setattr(user, k, v)
        created = False
    else:
        user = User(login=login, email=email, telephone=telephone, **defaults)
        created = True
    return user, created


def run_seed_demo_accounts():
    print("\n=========================================================")
    print("=== CRÉATION / SYNCHRONISATION DES COMPTES DE DÉMO ===")
    print("=========================================================")

    # 1. Super Administrateur
    admin_user, created = get_or_create_resilient_user(
        login="admin",
        email="direction@santenumerique.com",
        telephone="+224620000001",
        defaults={
            "nom": "Direction",
            "prenom": "Admin",
            "role": User.Role.ADMINISTRATEUR,
            "actif": True,
            "is_staff": True,
            "is_superuser": True,
        }
    )
    admin_user.set_password(DEMO_PASSWORD)
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.actif = True
    admin_user.save()
    status = "Créé" if created else "Mis à jour"
    print(f" [OK] {status} : Administrateur -> login: admin | email: direction@santenumerique.com | mdp: {DEMO_PASSWORD}")

    # 2. Médecin 1 : Dr. Mohamed Camara (Cardiologue)
    med_user1, created = get_or_create_resilient_user(
        login="dr.camara",
        email="dr.camara@santenumerique.com",
        telephone="+224621111111",
        defaults={
            "nom": "Camara",
            "prenom": "Mohamed",
            "role": User.Role.MEDECIN,
            "actif": True,
        }
    )
    med_user1.set_password(DEMO_PASSWORD)
    med_user1.actif = True
    med_user1.save()
    med1 = Medecin.objects.filter(id_utilisateur=med_user1).first()
    if not med1:
        med1 = Medecin.objects.create(
            id_utilisateur=med_user1,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numero_ordre="CNOM-75012",
            telephone_pro="+224621111111",
            email_pro="dr.camara@santenumerique.com",
            bureau="Cabinet 101 - Cardiologie",
            date_embauche="2023-01-10",
        )
    print(f" [OK] Médecin : Dr. Mohamed Camara -> login: dr.camara | mdp: {DEMO_PASSWORD} (Cardiologie)")

    # 3. Médecin 2 : Dr. Fatoumata Diallo (Pédiatrie)
    med_user2, created = get_or_create_resilient_user(
        login="dr.diallo",
        email="dr.diallo@santenumerique.com",
        telephone="+224622222222",
        defaults={
            "nom": "Diallo",
            "prenom": "Fatoumata",
            "role": User.Role.MEDECIN,
            "actif": True,
        }
    )
    med_user2.set_password(DEMO_PASSWORD)
    med_user2.actif = True
    med_user2.save()
    med2 = Medecin.objects.filter(id_utilisateur=med_user2).first()
    if not med2:
        med2 = Medecin.objects.create(
            id_utilisateur=med_user2,
            specialite=Medecin.Specialite.PEDIATRIE,
            numero_ordre="CNOM-82045",
            telephone_pro="+224622222222",
            email_pro="dr.diallo@santenumerique.com",
            bureau="Cabinet 102 - Pédiatrie",
            date_embauche="2023-06-01",
        )
    print(f" [OK] Médecin : Dr. Fatoumata Diallo -> login: dr.diallo | mdp: {DEMO_PASSWORD} (Pédiatrie)")

    # 4. Patient 1 : Amadou Sow
    pat_user1, created = get_or_create_resilient_user(
        login="patient.amadou",
        email="amadou.sow@santenumerique.com",
        telephone="+224623333333",
        defaults={
            "nom": "Sow",
            "prenom": "Amadou",
            "role": User.Role.PATIENT,
            "actif": True,
        }
    )
    pat_user1.set_password(DEMO_PASSWORD)
    pat_user1.actif = True
    pat_user1.save()
    pat1 = Patient.objects.filter(id_utilisateur=pat_user1).first()
    if not pat1:
        pat1 = Patient.objects.create(
            id_utilisateur=pat_user1,
            date_naissance="1988-04-12",
            sexe=Patient.Sexe.MASCULIN,
            adresse="12 Boulevard de la République, Conakry",
            groupe_sanguin=Patient.GroupeSanguin.O_POSITIF,
            numero_securite_sociale="1880412789123",
            personne_a_contacter="Aissatou Sow (+224623333334)",
            date_inscription="2024-01-15",
        )
    print(f" [OK] Patient : Amadou Sow -> login: patient.amadou | mdp: {DEMO_PASSWORD} (Groupe O+)")

    # Rendez-vous et ordonnances pour Amadou Sow
    from datetime import date, timedelta
    from rendezvous.models import RendezVous
    from consultation.models import Consultation
    from ordonnance.models import Ordonnance
    from ligne_ordonnance.models import LigneOrdonnance
    from notifications.models import NotificationHospitaliere

    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=2)

    rdv1, _ = RendezVous.objects.get_or_create(
        patient=pat1,
        medecin=med1,
        date_rdv=tomorrow,
        heure="10:30:00",
        defaults={
            "motif": "Consultation de contrôle et suivi cardiologique",
            "statut": RendezVous.StatutRendezVous.CONFIRME,
        }
    )

    cons1, _ = Consultation.objects.get_or_create(
        patient=pat1,
        medecin=med1,
        diagnostic="Hypertension artérielle modérée et surveillance rythmique",
        defaults={
            "symptomes": "Palpitations légères et essoufflement à l'effort",
            "observations": "Pression artérielle à 135/85 mmHg. Bilan sanguin normal. Traitement bien toléré.",
            "actif": True,
        }
    )

    ord1, _ = Ordonnance.objects.get_or_create(
        consultation=cons1,
        reference="ORD-2026-0842",
        defaults={
            "date_ordonnance": yesterday,
            "observation": "Traitement de fond cardiovasculaire. Respecter scrupuleusement les horaires de prise.",
            "actif": True,
        }
    )

    if not ord1.lignes.exists():
        LigneOrdonnance.objects.create(
            ordonnance=ord1,
            medicament="Cardensiel",
            dosage="5 mg",
            forme="Comprimé sécable",
            posologie="1 comprimé par jour, le matin au petit-déjeuner",
            duree_traitement="30 jours",
            quantite=1,
            instructions="Prendre avec un grand verre d'eau au réveil. Ne pas interrompre brutalement.",
            actif=True,
        )
        LigneOrdonnance.objects.create(
            ordonnance=ord1,
            medicament="Kardégic",
            dosage="75 mg",
            forme="Poudre pour solution buvable en sachet",
            posologie="1 sachet par jour au déjeuner",
            duree_traitement="30 jours",
            quantite=1,
            instructions="À dissoudre dans un demi-verre d'eau au milieu du repas.",
            actif=True,
        )
        LigneOrdonnance.objects.create(
            ordonnance=ord1,
            medicament="Paracétamol",
            dosage="1000 mg",
            forme="Comprimé",
            posologie="1 comprimé en cas de céphalées ou douleurs (max 3/jour)",
            duree_traitement="En cas de besoin",
            quantite=1,
            instructions="Espacer les prises de 6 heures minimum.",
            actif=True,
        )

    NotificationHospitaliere.objects.get_or_create(
        destinataire_user=pat_user1,
        type_notification="RAPPEL_RDV",
        titre="Rappel RDV : Consultation Cardiologie avec Dr. Mohamed Camara",
        defaults={
            "message": f"Votre rendez-vous est confirmé pour demain à 10h30 au Cabinet 101. Pensez à apporter vos ordonnances et résultats d'analyses récents.",
            "donnees": {
                "id_rdv": rdv1.id,
                "date_rdv": str(tomorrow),
                "heure": "10:30",
                "medecin": "Dr. Mohamed Camara",
                "bureau": "Cabinet 101 - Cardiologie"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.PATIENT,
            "lu": False,
        }
    )

    NotificationHospitaliere.objects.get_or_create(
        destinataire_user=pat_user1,
        type_notification="PRISE_MEDICAMENT",
        titre="Prise de médicament : Cardensiel 5 mg",
        defaults={
            "message": "1 comprimé le matin au petit-déjeuner. Traitement quotidien régulier (Ordonnance #ORD-2026-0842).",
            "donnees": {
                "medicament": "Cardensiel 5 mg",
                "posologie": "1 comprimé le matin",
                "duree": "30 jours",
                "reference": "ORD-2026-0842"
            },
            "destinataire_role": NotificationHospitaliere.DestinataireRole.PATIENT,
            "lu": False,
        }
    )

    # 5. Patient 2 : Mariama Barry
    pat_user2, created = get_or_create_resilient_user(
        login="patient.mariama",
        email="mariama.barry@santenumerique.com",
        telephone="+224624444444",
        defaults={
            "nom": "Barry",
            "prenom": "Mariama",
            "role": User.Role.PATIENT,
            "actif": True,
        }
    )
    pat_user2.set_password(DEMO_PASSWORD)
    pat_user2.actif = True
    pat_user2.save()
    pat2 = Patient.objects.filter(id_utilisateur=pat_user2).first()
    if not pat2:
        pat2 = Patient.objects.create(
            id_utilisateur=pat_user2,
            date_naissance="1994-09-22",
            sexe=Patient.Sexe.FEMININ,
            adresse="45 Avenue de l'Hôpital, Conakry",
            groupe_sanguin=Patient.GroupeSanguin.A_POSITIF,
            numero_securite_sociale="2940922456789",
            personne_a_contacter="Boubacar Barry (+224624444445)",
            date_inscription="2024-03-20",
        )
    print(f" [OK] Patient : Mariama Barry -> login: patient.mariama | mdp: {DEMO_PASSWORD} (Groupe A+)")

    # 6. Soignant / Infirmier : Sory Touré
    inf_user, created = get_or_create_resilient_user(
        login="infirmier.sory",
        email="sory.toure@santenumerique.com",
        telephone="+224625555555",
        defaults={
            "nom": "Touré",
            "prenom": "Sory",
            "role": User.Role.INFIRMIER,
            "actif": True,
        }
    )
    inf_user.set_password(DEMO_PASSWORD)
    inf_user.actif = True
    inf_user.save()
    inf_staff = Personnel.objects.filter(id_utilisateur=inf_user).first()
    if not inf_staff:
        inf_staff = Personnel.objects.create(
            id_utilisateur=inf_user,
            matricule="SOIGN-2024-001",
            type_personnel=Personnel.TypePersonnel.INFIRMIER,
            poste="Infirmier Diplômé d'État",
            date_embauche="2024-01-01",
        )
    print(f" [OK] Personnel Soignant : Sory Touré -> login: infirmier.sory | mdp: {DEMO_PASSWORD}")
    print("=========================================================\n")


if __name__ == "__main__":
    run_seed_demo_accounts()
