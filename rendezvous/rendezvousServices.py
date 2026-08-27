from datetime import date, time
from django.utils import timezone
from .models import RendezVous
from .rendezvousRepositories import RendezVousRepository


class ConflictError(Exception):
    """Exception levée en cas de conflit de créneau pour un médecin."""
    pass


class RendezVousService:
    # initialisation du repository pour avoir accès à ces données
    def __init__(self):
        self.repository = RendezVousRepository()

    # creation d'un rendez-vous avec vérification d'antériorité et d'absence de conflit
    def create_rendezvous(self, **data):
        date_rdv = data.get("date_rdv")
        heure = data.get("heure")
        medecin = data.get("medecin")

        # 1. Vérifier que la date et l'heure ne sont pas déjà passées
        if date_rdv and heure:
            now_dt = timezone.localtime()
            today = now_dt.date()
            current_time = now_dt.time()

            date_rdv_val = date.fromisoformat(date_rdv) if isinstance(date_rdv, str) else date_rdv
            heure_val = time.fromisoformat(heure) if isinstance(heure, str) else heure

            if date_rdv_val < today or (date_rdv_val == today and heure_val < current_time):
                raise ValueError("Impossible de programmer un rendez-vous à une date ou heure déjà passée.")

        # 2. Vérifier l'absence de conflit existant pour ce médecin
        if medecin and date_rdv and heure:
            conflit = RendezVous.objects.filter(
                medecin=medecin,
                date_rdv=date_rdv,
                heure=heure
            ).exclude(statut=RendezVous.StatutRendezVous.ANNULE).exists()

            if conflit:
                raise ConflictError("Ce médecin a déjà un rendez-vous programmé à cette date et cette heure.")

        return self.repository.create_rendezvous(**data)

    # rechercher un rendez-vous par son id

    def get_rendezvous(self, rdv_id):
        return self.repository.get_rendezvous(rdv_id)

    #  afficher tous les rendez-vous

    def get_all_rendezvous(self):
        return self.repository.get_all_rendezvous()

    # afficher le rendez-vous d'un patient 

    def get_rendezvous_by_patient(self, patient_id):
        return self.repository.get_rendezvous_by_patient(patient_id)

    #  afficher les rendez-vous d'un medecin 

    def get_rendezvous_by_medecin(self, medecin_id):
        return self.repository.get_rendezvous_by_medecin(medecin_id)

    # afficher les statuts des différents rendez-vous 

    def get_rendezvous_by_statut(self, statut):
        return self.repository.get_rendezvous_by_statut(statut)

    # afficher les rendez-vous d'une date 

    def get_rendezvous_by_date(self, date_rdv):
        return self.repository.get_rendezvous_by_date(date_rdv)

    # rechercher un rendez-vous

    def search_rendezvous(self, query):
        return self.repository.search_rendezvous(query)

    # mettre a jour les informations d'un rendez-vous 

    def update_rendezvous(self, rdv, **data):
        return self.repository.update_rendezvous(rdv, **data)

    # Annuler ou supprimer un rendez-vous
    def delete_rendezvous(self, rdv, hard=False):
        return self.repository.delete_rendezvous(rdv, hard=hard)

