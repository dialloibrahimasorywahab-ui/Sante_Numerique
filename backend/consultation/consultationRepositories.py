from typing import Optional
from django.utils import timezone
from .models import Consultation


class ConsultationRepository:

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
        return Consultation.objects.create(
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
        try:
            return Consultation.objects.select_related(
                'patient__id_utilisateur',
                'medecin__id_utilisateur',
                'rdv',
                'frais'
            ).prefetch_related('ordonnances').get(pk=consultation_id)
        except Consultation.DoesNotExist:
            return None

    def get_all_consultations(self, actif_only: bool = True):
        qs = Consultation.objects.select_related(
            'patient__id_utilisateur',
            'medecin__id_utilisateur',
            'rdv',
            'frais'
        ).prefetch_related('ordonnances').all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_consultations_by_patient(self, patient_id: int, actif_only: bool = True):
        return self.get_all_consultations(actif_only=actif_only).filter(patient_id=patient_id)

    def get_consultations_by_medecin(self, medecin_id: int, actif_only: bool = True):
        return self.get_all_consultations(actif_only=actif_only).filter(medecin_id=medecin_id)

    def update_consultation(self, consultation_id: int, **kwargs) -> Optional[Consultation]:
        cons = self.get_consultation_by_id(consultation_id)
        if not cons:
            return None
        for key, value in kwargs.items():
            if hasattr(cons, key):
                setattr(cons, key, value)
        cons.save()
        return cons

    def delete_consultation(self, consultation_id: int, hard: bool = False) -> bool:
        cons = self.get_consultation_by_id(consultation_id)
        if not cons:
            return False
        if hard:
            cons.delete()
        else:
            cons.actif = False
            cons.save()
        return True
