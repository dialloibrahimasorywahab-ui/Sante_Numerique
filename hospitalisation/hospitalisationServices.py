from typing import Optional
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

        if lit and statut == Hospitalisation.StatutHospitalisation.EN_COURS:
            lit.etat = Lit.EtatLit.OCCUPE
            lit.save()

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
        hospitalisation = self.repository.get_hospitalisation_by_id(hospitalisation_id)
        if not hospitalisation:
            return None

        nouveau_lit = kwargs.get('lit', hospitalisation.lit)
        nouveau_statut = kwargs.get('statut', hospitalisation.statut)
        nouvelle_date_entree = kwargs.get('date_entree', hospitalisation.date_entree)
        nouvelle_date_sortie = kwargs.get('date_sortie', hospitalisation.date_sortie)

        if nouvelle_date_entree and nouvelle_date_sortie and nouvelle_date_sortie < nouvelle_date_entree:
            raise ValueError("La date de sortie ne peut pas être antérieure à la date d'entrée.")

        # Libérer l'ancien lit si changement de lit ou si statut devient TERMINEE/ANNULEE
        ancien_lit = hospitalisation.lit
        if ancien_lit and (ancien_lit != nouveau_lit or nouveau_statut in [
            Hospitalisation.StatutHospitalisation.TERMINEE,
            Hospitalisation.StatutHospitalisation.ANNULEE
        ]):
            ancien_lit.etat = Lit.EtatLit.DISPONIBLE
            ancien_lit.save()

        # Marquer le nouveau lit comme occupé si hospitalisation est EN_COURS
        if nouveau_lit and nouveau_statut == Hospitalisation.StatutHospitalisation.EN_COURS:
            nouveau_lit.etat = Lit.EtatLit.OCCUPE
            nouveau_lit.save()

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
        hospitalisation = self.repository.get_hospitalisation_by_id(hospitalisation_id)
        if not hospitalisation:
            return False

        if hospitalisation.lit and hospitalisation.lit.etat == Lit.EtatLit.OCCUPE:
            hospitalisation.lit.etat = Lit.EtatLit.DISPONIBLE
            hospitalisation.lit.save()

        return self.repository.delete_hospitalisation(hospitalisation_id, hard=hard)
