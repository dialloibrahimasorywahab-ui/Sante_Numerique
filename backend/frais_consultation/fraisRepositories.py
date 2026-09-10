from typing import Optional
from common.repositories import BaseRepository
from .models import FraisConsultation


class FraisConsultationRepository(BaseRepository[FraisConsultation]):

    def __init__(self):
        super().__init__(model=FraisConsultation)

    def create_frais(
        self,
        montant: float,
        description: Optional[str] = None,
        statut: str = FraisConsultation.StatutPaiement.EN_ATTENTE,
        date_paiement=None,
    ) -> FraisConsultation:
        return self.create(
            montant=montant,
            description=description,
            statut=statut,
            date_paiement=date_paiement,
            actif=True,
        )

    def get_frais_by_id(self, frais_id: int) -> Optional[FraisConsultation]:
        return self.get_by_id(frais_id)

    def get_all_frais(self, actif_only: bool = True):
        return self.get_all(actif_only=actif_only)

    def update_frais(self, frais_id: int, **kwargs) -> Optional[FraisConsultation]:
        frais = self.get_frais_by_id(frais_id)
        if not frais:
            return None
        return self.update(frais, **kwargs)

    def delete_frais(self, frais_id: int, hard: bool = False) -> bool:
        frais = self.get_frais_by_id(frais_id)
        if not frais:
            return False
        if hard:
            return self.delete(frais, hard=True)
        else:
            frais.actif = False
            frais.statut = FraisConsultation.StatutPaiement.ANNULE
            frais.save()
            return True
