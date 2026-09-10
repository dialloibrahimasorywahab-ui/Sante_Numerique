from django.db.models import Q
from common.repositories import BaseRepository
from .models import RendezVous


class RendezVousRepository(BaseRepository[RendezVous]):

    def __init__(self):
        super().__init__(model=RendezVous)

    def create_rendezvous(self, **data):
        return self.create(**data)

    def get_rendezvous(self, rdv_id):
        return self.get_by_id(
            rdv_id,
            select_related=[
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            ]
        )

    def get_all_rendezvous(self):
        return self.model.objects.select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        ).all()

    def get_rendezvous_by_patient(self, patient_id):
        if not patient_id:
            return self.get_all_rendezvous()
        try:
            p_id = int(patient_id)
            return self.model.objects.filter(patient_id=p_id).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )
        except (ValueError, TypeError):
            clean_q = str(patient_id).strip()
            return self.model.objects.filter(
                Q(patient__id_utilisateur__nom__icontains=clean_q) |
                Q(patient__id_utilisateur__prenom__icontains=clean_q)
            ).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )

    def get_rendezvous_by_medecin(self, medecin_id):
        if not medecin_id:
            return self.get_all_rendezvous()
        try:
            m_id = int(medecin_id)
            return self.model.objects.filter(medecin_id=m_id).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )
        except (ValueError, TypeError):
            clean_q = str(medecin_id).strip()
            return self.model.objects.filter(
                Q(medecin__id_utilisateur__nom__icontains=clean_q) |
                Q(medecin__id_utilisateur__prenom__icontains=clean_q) |
                Q(medecin__matricule__icontains=clean_q)
            ).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )

    def get_rendezvous_by_statut(self, statut):
        if not statut:
            return self.get_all_rendezvous()
        clean_statut = str(statut).strip().upper().replace(" ", "_")
        return self.model.objects.filter(
            Q(statut__iexact=clean_statut) | Q(statut__icontains=clean_statut)
        ).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    def get_rendezvous_by_date(self, date_rdv):
        return self.model.objects.filter(date_rdv=date_rdv).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    def search_rendezvous(self, query):
        if not query:
            return self.get_all_rendezvous()
        clean_q = str(query).strip()
        return self.model.objects.filter(
            Q(motif__icontains=clean_q) |
            Q(patient__id_utilisateur__nom__icontains=clean_q) |
            Q(patient__id_utilisateur__prenom__icontains=clean_q) |
            Q(medecin__id_utilisateur__nom__icontains=clean_q) |
            Q(medecin__id_utilisateur__prenom__icontains=clean_q)
        ).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    def update_rendezvous(self, rdv, **data):
        return self.update(rdv, **data)

    def delete_rendezvous(self, rdv, hard=False):
        if hard:
            return self.delete(rdv, hard=True)
        else:
            rdv.statut = RendezVous.StatutRendezVous.ANNULE
            rdv.save()
            return True
