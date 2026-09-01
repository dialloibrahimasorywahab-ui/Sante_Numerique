from typing import Optional
from django.db import transaction
from django.utils import timezone
from lit.models import Lit
from .models import Hospitalisation
from .hospitalisationRepositories import HospitalisationRepository


class HospitalisationService:

    def __init__(self, repository: Optional[HospitalisationRepository] = None):
        self.repository = repository or HospitalisationRepository()

    def admettre_patient(
        self,
        patient,
        medecin=None,
        lit=None,
        date_entree=None,
        date_sortie=None,
        motif: Optional[str] = None,
        statut: str = Hospitalisation.StatutHospitalisation.EN_COURS,
        observation: Optional[str] = None,
    ) -> Hospitalisation:
        if date_entree and date_sortie and date_sortie < date_entree:
            raise ValueError("La date de sortie ne peut pas être antérieure à la date d'entrée.")

        with transaction.atomic():
            if lit:
                lit_locked = Lit.objects.select_for_update().get(pk=lit.pk)

                # Vérifier si une autre hospitalisation active occupe déjà ce lit
                active_hosp = Hospitalisation.objects.filter(
                    lit=lit_locked,
                    statut__in=[
                        Hospitalisation.StatutHospitalisation.EN_COURS,
                        Hospitalisation.StatutHospitalisation.PROGRAMMEE,
                    ],
                    actif=True
                ).exists()

                if lit_locked.etat != Lit.EtatLit.DISPONIBLE or active_hosp:
                    raise ValueError(f"Le lit {lit_locked.numero_lit or lit_locked.id} est actuellement indisponible ou déjà occupé (état : {lit_locked.get_etat_display()}).")

                if statut == Hospitalisation.StatutHospitalisation.EN_COURS:
                    lit_locked.etat = Lit.EtatLit.OCCUPE
                    lit_locked.save(update_fields=["etat"])
                    if lit_locked.chambre:
                        lit_locked.chambre.sync_statut()
                elif statut == Hospitalisation.StatutHospitalisation.PROGRAMMEE:
                    lit_locked.etat = Lit.EtatLit.RESERVE
                    lit_locked.save(update_fields=["etat"])
                    if lit_locked.chambre:
                        lit_locked.chambre.sync_statut()

                lit = lit_locked

            return self.repository.create_hospitalisation(
                patient=patient,
                medecin=medecin,
                lit=lit,
                date_entree=date_entree,
                date_sortie=date_sortie,
                motif=motif,
                statut=statut,
                observation=observation,
            )

    def mettre_a_jour_hospitalisation(
        self,
        hospitalisation_id: int,
        **kwargs
    ) -> Optional[Hospitalisation]:
        with transaction.atomic():
            hospitalisation = self.repository.get_hospitalisation_by_id(hospitalisation_id)
            if not hospitalisation:
                return None

            nouveau_lit = kwargs.get('lit', hospitalisation.lit)
            nouveau_statut = kwargs.get('statut', hospitalisation.statut)
            nouvelle_date_entree = kwargs.get('date_entree', hospitalisation.date_entree)
            nouvelle_date_sortie = kwargs.get('date_sortie', hospitalisation.date_sortie)

            if nouvelle_date_entree and nouvelle_date_sortie and nouvelle_date_sortie < nouvelle_date_entree:
                raise ValueError("La date de sortie ne peut pas être antérieure à la date d'entrée.")

            ancien_lit = hospitalisation.lit

            # Si changement de lit, vérifier la disponibilité du nouveau lit avec verrou
            if nouveau_lit and nouveau_lit != ancien_lit:
                nouveau_lit_locked = Lit.objects.select_for_update().get(pk=nouveau_lit.pk)
                active_hosp = Hospitalisation.objects.filter(
                    lit=nouveau_lit_locked,
                    statut__in=[
                        Hospitalisation.StatutHospitalisation.EN_COURS,
                        Hospitalisation.StatutHospitalisation.PROGRAMMEE,
                    ],
                    actif=True
                ).exclude(pk=hospitalisation_id).exists()

                if nouveau_lit_locked.etat != Lit.EtatLit.DISPONIBLE or active_hosp:
                    raise ValueError(f"Le lit {nouveau_lit_locked.numero_lit or nouveau_lit_locked.id} est actuellement indisponible ou déjà occupé (état : {nouveau_lit_locked.get_etat_display()}).")

                nouveau_lit = nouveau_lit_locked
                kwargs['lit'] = nouveau_lit

            # Libérer l'ancien lit si changement de lit ou si statut devient TERMINEE/ANNULEE
            if ancien_lit and (ancien_lit != nouveau_lit or nouveau_statut in [
                Hospitalisation.StatutHospitalisation.TERMINEE,
                Hospitalisation.StatutHospitalisation.ANNULEE
            ]):
                ancien_lit_locked = Lit.objects.select_for_update().get(pk=ancien_lit.pk)
                ancien_lit_locked.etat = Lit.EtatLit.DISPONIBLE
                ancien_lit_locked.save(update_fields=["etat"])
                if ancien_lit_locked.chambre:
                    ancien_lit_locked.chambre.sync_statut()

            # Marquer le nouveau lit selon le statut
            if nouveau_lit:
                nouveau_lit_locked = Lit.objects.select_for_update().get(pk=nouveau_lit.pk)
                if nouveau_statut == Hospitalisation.StatutHospitalisation.EN_COURS:
                    nouveau_lit_locked.etat = Lit.EtatLit.OCCUPE
                    nouveau_lit_locked.save(update_fields=["etat"])
                    if nouveau_lit_locked.chambre:
                        nouveau_lit_locked.chambre.sync_statut()
                elif nouveau_statut == Hospitalisation.StatutHospitalisation.PROGRAMMEE:
                    nouveau_lit_locked.etat = Lit.EtatLit.RESERVE
                    nouveau_lit_locked.save(update_fields=["etat"])
                    if nouveau_lit_locked.chambre:
                        nouveau_lit_locked.chambre.sync_statut()

            if nouveau_statut in [Hospitalisation.StatutHospitalisation.TERMINEE, Hospitalisation.StatutHospitalisation.ANNULEE]:
                if 'date_sortie' not in kwargs or not kwargs['date_sortie']:
                    kwargs['date_sortie'] = timezone.now()

            return self.repository.update_hospitalisation(hospitalisation_id, **kwargs)

    def cloturer_hospitalisation(self, hospitalisation_id: int, observation_finale: Optional[str] = None) -> Optional[Hospitalisation]:
        hospitalisation = self.repository.get_hospitalisation_by_id(hospitalisation_id)
        if not hospitalisation:
            return None

        update_kwargs = {
            'statut': Hospitalisation.StatutHospitalisation.TERMINEE,
            'date_sortie': timezone.now(),
        }
        if observation_finale:
            old_obs = hospitalisation.observation or ""
            update_kwargs['observation'] = f"{old_obs}\n[Clôture]: {observation_finale}".strip()

        return self.mettre_a_jour_hospitalisation(hospitalisation_id, **update_kwargs)

    def supprimer_hospitalisation(self, hospitalisation_id: int, hard: bool = False) -> bool:
        with transaction.atomic():
            hospitalisation = self.repository.get_hospitalisation_by_id(hospitalisation_id)
            if not hospitalisation:
                return False

            if hospitalisation.lit:
                lit_locked = Lit.objects.select_for_update().get(pk=hospitalisation.lit.pk)
                lit_locked.etat = Lit.EtatLit.DISPONIBLE
                lit_locked.save(update_fields=["etat"])
                if lit_locked.chambre:
                    lit_locked.chambre.sync_statut()

            return self.repository.delete_hospitalisation(hospitalisation_id, hard=hard)
