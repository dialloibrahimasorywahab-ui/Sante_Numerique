from typing import Optional
from django.utils import timezone
from common.repositories import BaseRepository
from .models import Ordonnance


class OrdonnanceRepository(BaseRepository[Ordonnance]):

    def __init__(self):
        super().__init__(model=Ordonnance)

    def create_ordonnance(
        self,
        consultation,
        reference: Optional[str] = None,
        date_ordonnance=None,
        observation: Optional[str] = None,
    ) -> Ordonnance:
        if not reference:
            today_str = timezone.now().strftime('%Y%m%d')
            count = Ordonnance.objects.filter(reference__startswith=f"ORD-{today_str}").count() + 1
            reference = f"ORD-{today_str}-{count:03d}"

        return self.create(
            consultation=consultation,
            reference=reference,
            date_ordonnance=date_ordonnance or timezone.now().date(),
            observation=observation,
            actif=True,
        )

    def get_ordonnance_by_id(self, ordonnance_id: int) -> Optional[Ordonnance]:
        return self.get_by_id(
            ordonnance_id,
            select_related=[
                'consultation__patient__id_utilisateur',
                'consultation__medecin__id_utilisateur'
            ],
            prefetch_related=['lignes']
        )

    def get_all_ordonnances(self, actif_only: bool = True):
        return self.get_all(
            actif_only=actif_only,
            select_related=[
                'consultation__patient__id_utilisateur',
                'consultation__medecin__id_utilisateur'
            ],
            prefetch_related=['lignes']
        )

    def get_ordonnances_by_consultation(self, consultation_id: int, actif_only: bool = True):
        return self.get_all_ordonnances(actif_only=actif_only).filter(consultation_id=consultation_id)

    def update_ordonnance(self, ordonnance_id: int, **kwargs) -> Optional[Ordonnance]:
        ord_obj = self.get_ordonnance_by_id(ordonnance_id)
        if not ord_obj:
            return None
        return self.update(ord_obj, **kwargs)

    def delete_ordonnance(self, ordonnance_id: int, hard: bool = False) -> bool:
        ord_obj = self.get_ordonnance_by_id(ordonnance_id)
        if not ord_obj:
            return False
        return self.delete(ord_obj, hard=hard)
