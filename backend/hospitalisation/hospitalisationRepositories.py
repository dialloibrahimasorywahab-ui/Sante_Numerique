from typing import Optional
# pyrefly: ignore [missing-import]
from django.utils import timezone
from .models import Hospitalisation


class HospitalisationRepository:

    def create_hospitalisation(
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
        return Hospitalisation.objects.create(
            patient=patient,
            medecin=medecin,
            lit=lit,
            date_entree=date_entree or timezone.now(),
            date_sortie=date_sortie,
            motif=motif,
            statut=statut,
            observation=observation,
            actif=True,
        )

    def get_hospitalisation_by_id(self, hospitalisation_id: int) -> Optional[Hospitalisation]:
        try:
            return Hospitalisation.objects.select_related(
                'patient__idUtilisateur',
                'medecin__idUtilisateur',
                'lit__chambre__batiment'
            ).get(pk=hospitalisation_id)
        except Hospitalisation.DoesNotExist:
            return None

    def get_all_hospitalisations(self, actif_only: bool = True):
        qs = Hospitalisation.objects.select_related(
            'patient__idUtilisateur',
            'medecin__idUtilisateur',
            'lit__chambre__batiment'
        ).all()
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_hospitalisations_by_patient(self, patient_id: int, actif_only: bool = True):
        return self.get_all_hospitalisations(actif_only=actif_only).filter(patient_id=patient_id)

    def get_hospitalisations_by_medecin(self, medecin_id: int, actif_only: bool = True):
        return self.get_all_hospitalisations(actif_only=actif_only).filter(medecin_id=medecin_id)

    def get_hospitalisations_by_lit(self, lit_id: int, actif_only: bool = True):
        return self.get_all_hospitalisations(actif_only=actif_only).filter(lit_id=lit_id)

    def get_hospitalisations_by_statut(self, statut: str, actif_only: bool = True):
        return self.get_all_hospitalisations(actif_only=actif_only).filter(statut=statut)

    def update_hospitalisation(self, hospitalisation_id: int, **kwargs) -> Optional[Hospitalisation]:
        hospitalisation = self.get_hospitalisation_by_id(hospitalisation_id)
        if not hospitalisation:
            return None
        for key, value in kwargs.items():
            if hasattr(hospitalisation, key):
                setattr(hospitalisation, key, value)
        hospitalisation.save()
        return hospitalisation

    def delete_hospitalisation(self, hospitalisation_id: int, hard: bool = False) -> bool:
        hospitalisation = self.get_hospitalisation_by_id(hospitalisation_id)
        if not hospitalisation:
            return False
        if hard:
            hospitalisation.delete()
        else:
            hospitalisation.actif = False
            hospitalisation.statut = Hospitalisation.StatutHospitalisation.ANNULEE
            hospitalisation.save()
        return True
