import os
import random
import django

# Initialisation du contexte Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User
from personnel.models import Personnel
from personnel.personnelServices import PersonnelService
from services.serviceServices import ServiceService


PERSONNEL_MEDICAL_DATA = [
    {
        "nom": "Camara",
        "prenom": "Aminata",
        "typePersonnel": Personnel.TypePersonnel.INFIRMIER,
        "poste": "Infirmière Major",
        "serviceHopital": "URGENCES",
        "matricule": "EMP-INF-001",
        "dateEmbauche": "2024-01-15",
    },
    {
        "nom": "Diallo",
        "prenom": "Mamadou Lamine",
        "typePersonnel": Personnel.TypePersonnel.TECHNICIEN,
        "poste": "Technicien supérieur de laboratoire",
        "serviceHopital": "LABORATOIRE",
        "matricule": "EMP-TEC-002",
        "dateEmbauche": "2023-09-01",
    },
    {
        "nom": "Sylla",
        "prenom": "Fatoumata Binta",
        "typePersonnel": Personnel.TypePersonnel.PHARMACIEN,
        "poste": "Pharmacienne Hospitalière",
        "serviceHopital": "PHARMACIE",
        "matricule": "EMP-PHA-003",
        "dateEmbauche": "2022-05-10",
    },
    {
        "nom": "Soumah",
        "prenom": "Kadiatou",
        "typePersonnel": Personnel.TypePersonnel.SAGE_FEMME,
        "poste": "Sage-Femme Principale",
        "serviceHopital": "MATERNITE",
        "matricule": "EMP-SF-004",
        "dateEmbauche": "2024-03-20",
    },
    {
        "nom": "Keita",
        "prenom": "Ousmane",
        "typePersonnel": Personnel.TypePersonnel.ADMINISTRATIF,
        "poste": "Chef du Service d'Admission",
        "serviceHopital": "ADMINISTRATION",
        "matricule": "EMP-ADM-005",
        "dateEmbauche": "2021-11-01",
    },
    {
        "nom": "Barry",
        "prenom": "Aissatou",
        "typePersonnel": Personnel.TypePersonnel.INFIRMIER,
        "poste": "Infirmière de Bloc Opératoire",
        "serviceHopital": "CHIRURGIE",
        "matricule": "EMP-INF-006",
        "dateEmbauche": "2025-01-05",
    },
    {
        "nom": "Traoré",
        "prenom": "Ibrahima Sory",
        "typePersonnel": Personnel.TypePersonnel.TECHNICIEN,
        "poste": "Radiologue & Technicien IRM",
        "serviceHopital": "RADIOLOGIE",
        "matricule": "EMP-TEC-007",
        "dateEmbauche": "2023-04-12",
    },
]


def register_medical_staff():
    service_svc = ServiceService()
    personnel_service = PersonnelService()

    print("=== Initialisation du Dictionnaire des Services Hospitaliers ===")
    services = service_svc.seed_default_services()
    print(f"[OK] {len(services)} services enregistrés dans le dictionnaire !")

    print("\n=== Début de l'enregistrement du Personnel Médical ===")

    registered_count = 0
    for i, data in enumerate(PERSONNEL_MEDICAL_DATA, start=1):
        clean_prenom = data["prenom"].split()[0].lower()
        clean_nom = data["nom"].lower()
        
        # Vérifier si un membre existe déjà par matricule
        existing_personnel = Personnel.objects.filter(matricule=data["matricule"]).first()
        if existing_personnel:
            # Mettre à jour avec le service et idService
            updated = personnel_service.update_personnel(
                existing_personnel,
                serviceHopital=data["serviceHopital"],
                poste=data["poste"]
            )
            registered_count += 1
            service_id_str = f"ID Service: {updated.idService.idService}" if updated.idService else "Pas de service"
            print(
                f"[{i}/{len(PERSONNEL_MEDICAL_DATA)}] [UPDATE] Mis à jour : "
                f"{updated.get_typePersonnel_display()} - {updated.idUtilisateur.prenom} {updated.idUtilisateur.nom} | "
                f"{service_id_str} ({updated.serviceHopital}) | Matricule: {updated.matricule}"
            )
            continue

        login = f"staff_{clean_prenom}_{clean_nom}_{random.randint(1000, 9999)}"
        email = f"{login}@santenumerique.com"
        telephone = f"+22462{random.randint(1000000, 9999999)}"

        payload = {
            "nom": data["nom"],
            "prenom": data["prenom"],
            "email": email,
            "telephone": telephone,
            "login": login,
            "motDePasse": f"PersonnelPass2026_{i}!",
            "typePersonnel": data["typePersonnel"],
            "poste": data["poste"],
            "serviceHopital": data["serviceHopital"],
            "matricule": data["matricule"],
            "dateEmbauche": data["dateEmbauche"],
        }

        try:
            personnel = personnel_service.createPersonnel(**payload)
            registered_count += 1
            service_id_str = f"ID Service: {personnel.idService.idService}" if personnel.idService else "Pas de service"
            print(
                f"[{i}/{len(PERSONNEL_MEDICAL_DATA)}] [OK] Succès : "
                f"{personnel.get_typePersonnel_display()} - {personnel.idUtilisateur.prenom} {personnel.idUtilisateur.nom} | "
                f"{service_id_str} ({personnel.serviceHopital}) | Matricule: {personnel.matricule} | Login: {login}"
            )
        except Exception as error:
            print(f"[{i}/{len(PERSONNEL_MEDICAL_DATA)}] [ERREUR] Échec de l'enregistrement pour {data['prenom']} {data['nom']}: {error}")

    print(f"\n[Terminé] {registered_count}/{len(PERSONNEL_MEDICAL_DATA)} membres du personnel médical ont été traités et enregistrés avec succès !")


if __name__ == "__main__":
    register_medical_staff()
