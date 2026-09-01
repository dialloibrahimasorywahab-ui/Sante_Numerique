from typing import Optional
from .models import Ordonnance
from .ordonnanceRepositories import OrdonnanceRepository


class OrdonnanceService:

    def __init__(self, repository: Optional[OrdonnanceRepository] = None):
        self.repository = repository or OrdonnanceRepository()

    def prescrire_ordonnance(
        self,
        consultation,
        reference: Optional[str] = None,
        date_ordonnance=None,
        observation: Optional[str] = None,
    ) -> Ordonnance:
        return self.repository.create_ordonnance(
            consultation=consultation,
            reference=reference,
            date_ordonnance=date_ordonnance,
            observation=observation,
        )

    def mettre_a_jour_ordonnance(self, ordonnance_id: int, **kwargs) -> Optional[Ordonnance]:
        return self.repository.update_ordonnance(ordonnance_id, **kwargs)

    def supprimer_ordonnance(self, ordonnance_id: int, hard: bool = False) -> bool:
        return self.repository.delete_ordonnance(ordonnance_id, hard=hard)
