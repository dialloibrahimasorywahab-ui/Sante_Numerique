# pyrefly: ignore [missing-import]
from django.db.models import Q
from .models import RendezVous


class RendezVousRepository:
    # creer un rendez vous
    def create_rendezvous(self, **data):
        return RendezVous.objects.create(**data)

    #  afficher un rendez-vous grace a son id

    def get_rendezvous(self, rdv_id):
        try:
            return RendezVous.objects.select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            ).get(id=rdv_id)
        except RendezVous.DoesNotExist:
            return None

    # afficher tous les rendez-vous 

    def get_all_rendezvous(self):
        return RendezVous.objects.select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        ).all()

    # afficher les rendez-vous d'un patient

    def get_rendezvous_by_patient(self, patient_id):
        if not patient_id:
            return self.get_all_rendezvous()
        try:
            p_id = int(patient_id)
            return RendezVous.objects.filter(patient_id=p_id).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )
        except (ValueError, TypeError):
            clean_q = str(patient_id).strip()
            return RendezVous.objects.filter(
                Q(patient__id_utilisateur__nom__icontains=clean_q) |
                Q(patient__id_utilisateur__prenom__icontains=clean_q)
            ).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )

    # afficher les rendez-vous d'un medecin 

    def get_rendezvous_by_medecin(self, medecin_id):
        if not medecin_id:
            return self.get_all_rendezvous()
        try:
            m_id = int(medecin_id)
            return RendezVous.objects.filter(medecin_id=m_id).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )
        except (ValueError, TypeError):
            clean_q = str(medecin_id).strip()
            return RendezVous.objects.filter(
                Q(medecin__id_utilisateur__nom__icontains=clean_q) |
                Q(medecin__id_utilisateur__prenom__icontains=clean_q) |
                Q(medecin__matricule__icontains=clean_q)
            ).select_related(
                'patient', 'patient__id_utilisateur',
                'medecin', 'medecin__id_utilisateur'
            )

    # afficher les rendez-vous par leurs statut

    def get_rendezvous_by_statut(self, statut):
        if not statut:
            return self.get_all_rendezvous()
        clean_statut = str(statut).strip().upper().replace(" ", "_")
        return RendezVous.objects.filter(
            Q(statut__iexact=clean_statut) | Q(statut__icontains=clean_statut)
        ).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    # afficher les rendez-vous d'une date

    def get_rendezvous_by_date(self, date_rdv):
        return RendezVous.objects.filter(date_rdv=date_rdv).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    # rechercher un rendez-vous par les query

    def search_rendezvous(self, query):
        if not query:
            return self.get_all_rendezvous()
        clean_q = str(query).strip()
        return RendezVous.objects.filter(
            Q(motif__icontains=clean_q) |
            Q(patient__id_utilisateur__nom__icontains=clean_q) |
            Q(patient__id_utilisateur__prenom__icontains=clean_q) |
            Q(medecin__id_utilisateur__nom__icontains=clean_q) |
            Q(medecin__id_utilisateur__prenom__icontains=clean_q)
        ).select_related(
            'patient', 'patient__id_utilisateur',
            'medecin', 'medecin__id_utilisateur'
        )

    # mettre à jour les informations d'un rendez-vous

    def update_rendezvous(self, rdv, **data):
        for field, value in data.items():
            setattr(rdv, field, value)
        rdv.save()
        return rdv

    def delete_rendezvous(self, rdv, hard=False):
        if hard:
            rdv.delete()
        else:
            rdv.statut = RendezVous.StatutRendezVous.ANNULE
            rdv.save()

