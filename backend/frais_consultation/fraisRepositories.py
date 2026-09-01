from typing import Optional
from django.utils import timezone
from .models import FraisConsultation


class FraisConsultationRepository:

    def create_frais(
        self,
        montant: float,
        description: Optional[str] = None,
        statut: str = FraisConsultation.StatutPaiement.EN_ATTENTE,
        date_paiement=None,
    ) -> FraisConsultation:
        return FraisConsultation.objects.create(
            montant=montant,
            description=description,
            statut=statut,
            date_paiement=date_paiement,
            actif=True,
        )

    def get_frais_by_id(self, frais_id: int) -> Optional[FraisConsultation]:
        try:
            return FraisConsultation.objects.get(pk=frais_id)
        except FraisConsultation.DoesNotExist:
            return None

    def get_all_frais(self, actif_only: bool = True):
        qs = FraisConsultation.objects.all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def update_frais(self, frais_id: int, **kwargs) -> Optional[FraisConsultation]:
        frais = self.get_frais_by_id(frais_id)
        if not frais:
            return None
        for key, value in kwargs.items():
            if hasattr(frais, key):
                setattr(frais, key, value)
        frais.save()
        return frais

    def delete_frais(self, frais_id: int, hard: bool = False) -> bool:
        frais = self.get_frais_by_id(frais_id)
        if not frais:
            return False
        if hard:
            frais.delete()
        else:
            frais.actif = False
            frais.statut = FraisConsultation.StatutPaiement.ANNULE
            frais.save()
        return True
