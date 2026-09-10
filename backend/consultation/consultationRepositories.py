from typing import Optional
from django.utils import timezone
from common.repositories import BaseRepository
from .models import Consultation


class ConsultationRepository(BaseRepository[Consultation]):

    def __init__(self):
        super().__init__(model=Consultation)

    def create_consultation(
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
        return self.create(
            patient=patient,
            medecin=medecin,
            rdv=rdv,
            frais=frais,
            date_cons=date_cons or timezone.now(),
            symptomes=symptomes,
            diagnostic=diagnostic,
            observations=observations,
            actif=True,
        )

    def get_consultation_by_id(self, consultation_id: int) -> Optional[Consultation]:
        return self.get_by_id(
            consultation_id,
            select_related=[
                'patient__id_utilisateur',
                'medecin__id_utilisateur',
                'rdv',
                'frais'
            ],
            prefetch_related=['ordonnances']
        )

    def get_all_consultations(self, actif_only: bool = True):
        return self.get_all(
            actif_only=actif_only,
            select_related=[
                'patient__id_utilisateur',
                'medecin__id_utilisateur',
                'rdv',
                'frais'
            ],
            prefetch_related=['ordonnances']
        )

    def get_consultations_by_patient(self, patient_id: int, actif_only: bool = True):
        return self.get_all_consultations(actif_only=actif_only).filter(patient_id=patient_id)

    def get_consultations_by_medecin(self, medecin_id: int, actif_only: bool = True):
        return self.get_all_consultations(actif_only=actif_only).filter(medecin_id=medecin_id)

    def update_consultation(self, consultation_id: int, **kwargs) -> Optional[Consultation]:
        cons = self.get_consultation_by_id(consultation_id)
        if not cons:
            return None
        return self.update(cons, **kwargs)

    def delete_consultation(self, consultation_id: int, hard: bool = False) -> bool:
        cons = self.get_consultation_by_id(consultation_id)
        if not cons:
            return False
        return self.delete(cons, hard=hard)
