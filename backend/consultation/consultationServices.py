from typing import Optional
from django.db import transaction
from django.utils import timezone
from common.services import BaseService
from rendezvous.models import RendezVous
from .models import Consultation
from .consultationRepositories import ConsultationRepository


class ConsultationService(BaseService[Consultation]):

    def __init__(self, repository: Optional[ConsultationRepository] = None):
        self.repository = repository or ConsultationRepository()
        super().__init__(repository=self.repository)

    def creer_consultation(
        self,
        patient,
        medecin=None,
        rdv=None,
        frais=None,
        montant_frais=None,
        description_frais: Optional[str] = None,
        date_cons=None,
        symptomes: Optional[str] = None,
        diagnostic: Optional[str] = None,
        observations: Optional[str] = None,
    ) -> Consultation:
        with transaction.atomic():
            if rdv:
                patient_id_val = patient.pk if hasattr(patient, 'pk') else getattr(patient, 'idPatient', getattr(patient, 'id', patient))
                if rdv.patient_id != patient_id_val:
                    raise ValueError("Le rendez-vous sélectionné n'appartient pas à ce patient.")
                if rdv.statut != RendezVous.StatutRendezVous.TERMINE:
                    rdv.statut = RendezVous.StatutRendezVous.TERMINE
                    rdv.save(update_fields=["statut"])

            # Si le médecin a saisi un montant de frais directement
            if montant_frais is not None and frais is None:
                from frais_consultation.models import FraisConsultation
                frais = FraisConsultation.objects.create(
                    montant=montant_frais,
                    description=description_frais or "Frais de consultation médicale",
                    statut=FraisConsultation.StatutPaiement.EN_ATTENTE
                )

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

            return consultation

    def mettre_a_jour_consultation(self, consultation_id: int, **kwargs) -> Optional[Consultation]:
        with transaction.atomic():
            montant_frais = kwargs.pop('montant_frais', None)
            description_frais = kwargs.pop('description_frais', None)

            cons = self.repository.get_consultation_by_id(consultation_id)
            if not cons:
                return None

            if montant_frais is not None:
                from frais_consultation.models import FraisConsultation
                if cons.frais:
                    cons.frais.montant = montant_frais
                    if description_frais is not None:
                        cons.frais.description = description_frais
                    cons.frais.save(update_fields=['montant', 'description'] if description_frais is not None else ['montant'])
                else:
                    new_frais = FraisConsultation.objects.create(
                        montant=montant_frais,
                        description=description_frais or "Frais de consultation médicale",
                        statut=FraisConsultation.StatutPaiement.EN_ATTENTE
                    )
                    kwargs['frais'] = new_frais

            return self.repository.update_consultation(consultation_id, **kwargs)

    def supprimer_consultation(self, consultation_id: int, hard: bool = False) -> bool:
        return self.repository.delete_consultation(consultation_id, hard=hard)
