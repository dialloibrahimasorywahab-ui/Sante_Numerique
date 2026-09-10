from datetime import date, time
from django.utils import timezone
from common.services import BaseService
from .models import RendezVous
from .rendezvousRepositories import RendezVousRepository


class ConflictError(Exception):
    """Exception levée en cas de conflit de créneau pour un médecin."""
    pass


class RendezVousService(BaseService[RendezVous]):

    def __init__(self):
        self.repository = RendezVousRepository()
        super().__init__(repository=self.repository)

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

    def get_rendezvous(self, rdv_id):
        return self.repository.get_rendezvous(rdv_id)

    def get_all_rendezvous(self):
        return self.repository.get_all_rendezvous()

    def get_rendezvous_by_patient(self, patient_id):
        return self.repository.get_rendezvous_by_patient(patient_id)

    def get_rendezvous_by_medecin(self, medecin_id):
        return self.repository.get_rendezvous_by_medecin(medecin_id)

    def get_rendezvous_by_statut(self, statut):
        return self.repository.get_rendezvous_by_statut(statut)

    def get_rendezvous_by_date(self, date_rdv):
        return self.repository.get_rendezvous_by_date(date_rdv)

    def search_rendezvous(self, query):
        return self.repository.search_rendezvous(query)

    def update_rendezvous(self, rdv, **data):
        return self.repository.update_rendezvous(rdv, **data)

    def delete_rendezvous(self, rdv, hard=False):
        return self.repository.delete_rendezvous(rdv, hard=hard)
