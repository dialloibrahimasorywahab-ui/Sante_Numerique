from typing import Optional
from django.utils import timezone
from rendezvous.models import RendezVous
from .models import Consultation
from .consultationRepositories import ConsultationRepository


class ConsultationService:

    def __init__(self, repository: Optional[ConsultationRepository] = None):
        self.repository = repository or ConsultationRepository()

    def creer_consultation(
        self,
        patient,
        medecin=None,
        rdv=None,
        frais=None,
        date_cons=None,
        symptomes: Optional[str] = None,
        diagnostic: Optional[str] = None,
        observations: Optional[str] = None,
    ) -> Consultation:
        consultation = self.repository.create_consultation(
            patient=patient,
            medecin=medecin,
            rdv=rdv,
            frais=frais,
            date_cons=date_cons,
            symptomes=symptomes,
            diagnostic=diagnostic,
            observations=observations,
        )

        # Marquer le RDV associé comme TERMINE si présent
        if rdv and rdv.statut != RendezVous.StatutRendezVous.TERMINE:
            rdv.statut = RendezVous.StatutRendezVous.TERMINE
            rdv.save()

        return consultation

    def mettre_a_jour_consultation(self, consultation_id: int, **kwargs) -> Optional[Consultation]:
        return self.repository.update_consultation(consultation_id, **kwargs)

    def supprimer_consultation(self, consultation_id: int, hard: bool = False) -> bool:
        return self.repository.delete_consultation(consultation_id, hard=hard)
