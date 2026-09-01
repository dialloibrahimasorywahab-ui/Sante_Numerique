# pyrefly: ignore [missing-import]
from typing import Optional
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
from .models import Ordonnance


class OrdonnanceRepository:

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

        return Ordonnance.objects.create(
            consultation=consultation,
            reference=reference,
            date_ordonnance=date_ordonnance or timezone.now().date(),
            observation=observation,
            actif=True,
        )

    def get_ordonnance_by_id(self, ordonnance_id: int) -> Optional[Ordonnance]:
        try:
            return Ordonnance.objects.select_related(
                'consultation__patient__id_utilisateur',
                'consultation__medecin__id_utilisateur'
            ).get(pk=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return None

    def get_all_ordonnances(self, actif_only: bool = True):
        qs = Ordonnance.objects.select_related(
            'consultation__patient__id_utilisateur',
            'consultation__medecin__id_utilisateur'
        ).all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_ordonnances_by_consultation(self, consultation_id: int, actif_only: bool = True):
        return self.get_all_ordonnances(actif_only=actif_only).filter(consultation_id=consultation_id)

    def update_ordonnance(self, ordonnance_id: int, **kwargs) -> Optional[Ordonnance]:
        ord_obj = self.get_ordonnance_by_id(ordonnance_id)
        if not ord_obj:
            return None
        for key, value in kwargs.items():
            if hasattr(ord_obj, key):
                setattr(ord_obj, key, value)
        ord_obj.save()
        return ord_obj

    def delete_ordonnance(self, ordonnance_id: int, hard: bool = False) -> bool:
        ord_obj = self.get_ordonnance_by_id(ordonnance_id)
        if not ord_obj:
            return False
        if hard:
            ord_obj.delete()
        else:
            ord_obj.actif = False
            ord_obj.save()
        return True
