import logging
import datetime
from typing import Optional
from django.utils import timezone
from django.db.models import QuerySet, Q
from .models import Sejour, DemandeAnalyse

logger = logging.getLogger(__name__)


class SejourRepository:
    """Accès aux données et requêtes optimisées pour les Séjours."""

    def get_queryset(self, actif_only: bool = True) -> QuerySet[Sejour]:
        qs = Sejour.objects.select_related(
            "patient",
            "patient__id_utilisateur",
            "service_responsable",
            "medecin_responsable",
            "medecin_responsable__id_utilisateur",
            "enregistre_par",
        ).prefetch_related(
            "localisations",
            "localisations__service",
            "localisations__batiment",
            "localisations__chambre",
            "localisations__lit",
            "mouvements",
            "evenements",
            "demandes_analyses",
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_by_id(self, sejour_id: int, actif_only: bool = True) -> Optional[Sejour]:
        try:
            return self.get_queryset(actif_only=actif_only).get(id_sejour=sejour_id)
        except Sejour.DoesNotExist:
            return None

    def get_by_reference(self, reference: str, actif_only: bool = True) -> Optional[Sejour]:
        try:
            return self.get_queryset(actif_only=actif_only).get(reference=reference)
        except Sejour.DoesNotExist:
            return None

    def get_all(
        self,
        patient_id: Optional[int] = None,
        service_id: Optional[int] = None,
        medecin_id: Optional[int] = None,
        statut: Optional[str] = None,
        type_prise_en_charge: Optional[str] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        search: Optional[str] = None,
        actif_only: bool = True,
    ) -> QuerySet[Sejour]:
        qs = self.get_queryset(actif_only=actif_only)

        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if service_id:
            qs = qs.filter(service_responsable_id=service_id)
        if medecin_id:
            qs = qs.filter(medecin_responsable_id=medecin_id)
        if statut:
            qs = qs.filter(statut=statut)
        if type_prise_en_charge:
            qs = qs.filter(type_prise_en_charge=type_prise_en_charge)
        if date_debut:
            qs = qs.filter(date_admission__gte=date_debut)
        if date_fin:
            qs = qs.filter(date_admission__lte=date_fin)
        if search:
            qs = qs.filter(
                Q(reference__icontains=search)
                | Q(motif_admission__icontains=search)
                | Q(patient__id_utilisateur__nom__icontains=search)
                | Q(patient__id_utilisateur__prenom__icontains=search)
                | Q(patient__numero_securite_sociale__icontains=search)
            )
        return qs

    def get_active_sejour_for_patient(self, patient_id: int) -> Optional[Sejour]:
        """Retourne le séjour en cours pour un patient, le cas échéant."""
        return (
            self.get_queryset(actif_only=True)
            .filter(
                patient_id=patient_id,
                statut__in=[
                    Sejour.StatutSejour.EN_ATTENTE,
                    Sejour.StatutSejour.EN_COURS,
                    Sejour.StatutSejour.TRANSFERE,
                    Sejour.StatutSejour.SORTIE_AUTORISEE,
                ],
            )
            .first()
        )

    def get_statistiques_dashboard(self) -> dict:
        from lit.models import Lit
        from mouvement.models import MouvementPatient
        import datetime

        hier = timezone.now() - datetime.timedelta(days=1)
        sejours_actifs = Sejour.objects.filter(
            actif=True,
            statut__in=[
                Sejour.StatutSejour.EN_ATTENTE,
                Sejour.StatutSejour.EN_COURS,
                Sejour.StatutSejour.TRANSFERE,
                Sejour.StatutSejour.SORTIE_AUTORISEE,
            ],
        )

        return {
            "patients_presents": sejours_actifs.count(),
            "sejours_en_cours": sejours_actifs.filter(statut=Sejour.StatutSejour.EN_COURS).count(),
            "patients_urgences": sejours_actifs.filter(
                Q(type_prise_en_charge=Sejour.TypePriseEnCharge.URGENCE)
                | Q(service_responsable__nom_service__icontains="urgenc")
            ).count(),
            "patients_hospitalises": sejours_actifs.filter(
                localisations__lit__isnull=False,
                localisations__est_actuelle=True,
            ).distinct().count(),
            "lits_occupes": Lit.objects.filter(etat="OCCUPE").count(),
            "lits_disponibles": Lit.objects.filter(etat="DISPONIBLE").count(),
            "total_lits": Lit.objects.count(),
            "transferts_recents": MouvementPatient.objects.filter(date_mouvement__gte=hier).count(),
            "sorties_recentes": Sejour.objects.filter(statut=Sejour.StatutSejour.TERMINE, date_sortie__gte=hier).count(),
            "timestamp": timezone.now().isoformat(),
        }


class DemandeAnalyseRepository:
    """Accès aux données pour les demandes d'examens / analyses."""

    def get_queryset(self, actif_only: bool = True) -> QuerySet[DemandeAnalyse]:
        qs = DemandeAnalyse.objects.select_related(
            "patient",
            "sejour",
            "prescripteur",
            "prescripteur__id_utilisateur",
        )
        if actif_only:
            qs = qs.filter(actif=True)
        return qs

    def get_by_id(self, analyse_id: int, actif_only: bool = True) -> Optional[DemandeAnalyse]:
        try:
            return self.get_queryset(actif_only=actif_only).get(id=analyse_id)
        except DemandeAnalyse.DoesNotExist:
            return None

    def get_all(
        self,
        sejour_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        statut: Optional[str] = None,
        actif_only: bool = True,
    ) -> QuerySet[DemandeAnalyse]:
        qs = self.get_queryset(actif_only=actif_only)
        if sejour_id:
            qs = qs.filter(sejour_id=sejour_id)
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if statut:
            qs = qs.filter(statut=statut)
        return qs
