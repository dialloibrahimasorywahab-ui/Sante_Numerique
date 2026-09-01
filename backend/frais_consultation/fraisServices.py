from typing import Optional
from django.utils import timezone
from .models import FraisConsultation
from .fraisRepositories import FraisConsultationRepository


class FraisConsultationService:

    def __init__(self, repository: Optional[FraisConsultationRepository] = None):
        self.repository = repository or FraisConsultationRepository()

    def creer_frais(
        self,
        montant: float,
        description: Optional[str] = None,
        statut: str = FraisConsultation.StatutPaiement.EN_ATTENTE,
    ) -> FraisConsultation:
        if montant < 0:
            raise ValueError("Le montant des frais ne peut pas être négatif.")
        date_paiement = timezone.now() if statut == FraisConsultation.StatutPaiement.PAYE else None
        return self.repository.create_frais(
            montant=montant,
            description=description,
            statut=statut,
            date_paiement=date_paiement,
        )

    def enregistrer_reglement(self, frais_id: int) -> Optional[FraisConsultation]:
        frais = self.repository.get_frais_by_id(frais_id)
        if not frais:
            return None
        return self.repository.update_frais(
            frais_id,
            statut=FraisConsultation.StatutPaiement.PAYE,
            date_paiement=timezone.now()
        )

    def mettre_a_jour_frais(self, frais_id: int, **kwargs) -> Optional[FraisConsultation]:
        frais = self.repository.get_frais_by_id(frais_id)
        if not frais:
            return None

        if 'montant' in kwargs and kwargs['montant'] < 0:
            raise ValueError("Le montant des frais ne peut pas être négatif.")

        if kwargs.get('statut') == FraisConsultation.StatutPaiement.PAYE and not frais.date_paiement:
            kwargs['date_paiement'] = timezone.now()

        return self.repository.update_frais(frais_id, **kwargs)

    def supprimer_frais(self, frais_id: int, hard: bool = False) -> bool:
        return self.repository.delete_frais(frais_id, hard=hard)
