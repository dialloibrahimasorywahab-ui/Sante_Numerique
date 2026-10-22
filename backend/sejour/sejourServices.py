import logging
from typing import Any, Dict, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Sejour, DemandeAnalyse
from .sejourRepositories import SejourRepository, DemandeAnalyseRepository

logger = logging.getLogger(__name__)


class SejourService:
    """Service métier gérant le cycle de vie du séjour d'un patient."""

    def __init__(self):
        self.repository = SejourRepository()
        self.analyse_repo = DemandeAnalyseRepository()

    @transaction.atomic
    def admettre_patient(self, data: Dict[str, Any], user=None) -> Sejour:
        """
        Admet un patient au sein de l'établissement :
        - Vérifie l'absence de séjour actif non clos pour ce patient.
        - Crée l'entité Sejour avec référence unique.
        - Crée la localisation initiale.
        - Enregistre un MouvementPatient d'admission.
        - Trace un EvenementParcours d'admission.
        """
        patient_id = data.get("patient_id") or data.get("patient")
        if not patient_id:
            raise ValidationError({"patient": "L'identifiant du patient est obligatoire pour l'admission."})

        # Vérifier si un séjour actif existe déjà
        sejour_actif = self.repository.get_active_sejour_for_patient(patient_id=int(patient_id))
        if sejour_actif:
            raise ValidationError({
                "patient": f"Le patient possède déjà un séjour actif en cours (Réf: {sejour_actif.reference}). Clôturez-le avant d'en créer un nouveau."
            })

        reference = data.get("reference")
        if not reference:
            reference = Sejour.generer_nouvelle_reference()
        elif Sejour.objects.filter(reference=reference).exists():
            raise ValidationError({"reference": f"La référence {reference} est déjà attribuée."})

        sejour = Sejour(
            reference=reference,
            patient_id=patient_id,
            service_responsable_id=data.get("service_responsable_id") or data.get("service_responsable") or data.get("serviceResponsable"),
            medecin_responsable_id=data.get("medecin_responsable_id") or data.get("medecin_responsable") or data.get("medecinResponsable"),
            enregistre_par=user,
            type_prise_en_charge=data.get("type_prise_en_charge", Sejour.TypePriseEnCharge.URGENCE),
            statut=data.get("statut", Sejour.StatutSejour.EN_COURS),
            date_admission=data.get("date_admission", timezone.now()),
            motif_admission=data.get("motif_admission", "Admission dans le service"),
        )
        sejour.full_clean()
        sejour.save()

        # Import différé des applications soeurs pour éviter les cycles
        from localisation.models import LocalisationPatient
        from mouvement.models import MouvementPatient
        from evenement.models import EvenementParcours

        # Création de la localisation initiale
        service_id = sejour.service_responsable_id
        batiment_id = data.get("batiment_id") or data.get("batiment")
        chambre_id = data.get("chambre_id") or data.get("chambre")
        lit_id = data.get("lit_id") or data.get("lit")

        # Si un lit est attribué dès l'admission, verrouiller et occuper
        if lit_id:
            from lit.models import Lit
            lit = Lit.objects.select_for_update().get(id=lit_id)
            if lit.etat != "DISPONIBLE":
                raise ValidationError({"lit": f"Le lit #{lit.id} n'est pas disponible (statut actuel: {lit.etat})."})
            lit.etat = "OCCUPE"
            lit.save(update_fields=["etat"])
            if not chambre_id:
                chambre_id = lit.chambre_id
            if chambre_id and not batiment_id:
                batiment_id = lit.chambre.batiment_id

        loc_initiale = LocalisationPatient.objects.create(
            sejour=sejour,
            service_id=service_id,
            batiment_id=batiment_id,
            chambre_id=chambre_id,
            lit_id=lit_id,
            date_debut=sejour.date_admission,
            est_actuelle=True,
            motif="Admission initiale",
            enregistre_par=user,
        )

        # Mouvement d'admission
        MouvementPatient.objects.create(
            sejour=sejour,
            localisation_origine=None,
            localisation_destination=loc_initiale,
            date_mouvement=sejour.date_admission,
            type_mouvement=MouvementPatient.TypeMouvement.ADMISSION,
            motif=sejour.motif_admission,
            enregistre_par=user,
        )

        # Timeline événement
        EvenementParcours.objects.create(
            sejour=sejour,
            type_evenement=EvenementParcours.TypeEvenement.ADMISSION,
            titre="Admission du patient",
            description=f"Admission en {sejour.get_type_prise_en_charge_display()} dans le service {sejour.service_responsable}. Motif: {sejour.motif_admission}",
            date_evenement=sejour.date_admission,
            declare_par=user,
            importance=EvenementParcours.NiveauImportance.INFO,
            donnees_additionnelles={"localisation_id": loc_initiale.id},
        )

        logger.info(f"Admission validée pour le patient #{patient_id} - Séjour {sejour.reference}")
        return sejour

    @transaction.atomic
    def autoriser_sortie(self, sejour_id: int, user=None, motif: Optional[str] = None) -> Sejour:
        """Marque la sortie comme médicalement autorisée par un praticien."""
        sejour = self.repository.get_by_id(sejour_id)
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        if sejour.statut in [Sejour.StatutSejour.TERMINE, Sejour.StatutSejour.ANNULE]:
            raise ValidationError({"statut": "Impossible d'autoriser la sortie d'un séjour déjà clos ou annulé."})

        sejour.statut = Sejour.StatutSejour.SORTIE_AUTORISEE
        sejour.motif_sortie = motif or sejour.motif_sortie
        sejour.save(update_fields=["statut", "motif_sortie", "updated_at"])

        from evenement.models import EvenementParcours
        EvenementParcours.objects.create(
            sejour=sejour,
            type_evenement=EvenementParcours.TypeEvenement.SORTIE_AUTORISEE,
            titre="Autorisation médicale de sortie",
            description=motif or "Sortie médicale autorisée par le praticien.",
            date_evenement=timezone.now(),
            declare_par=user,
            importance=EvenementParcours.NiveauImportance.INFO,
        )
        return sejour

    @transaction.atomic
    def enregistrer_sortie(
        self,
        sejour_id: int,
        user=None,
        date_sortie: Optional[Any] = None,
        motif_sortie: Optional[str] = None,
    ) -> Sejour:
        """
        Effectue la sortie administrative et physique définitive du patient :
        - Clôture le séjour (statut TERMINE).
        - Clôture la localisation active (date_fin, est_actuelle=False).
        - Libère le lit d'hospitalisation associé (DISPONIBLE).
        - Crée un mouvement de sortie définitive.
        - Émet l'événement final du parcours.
        """
        sejour = self.repository.get_by_id(sejour_id)
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        if sejour.statut == Sejour.StatutSejour.TERMINE:
            raise ValidationError({"statut": "Ce séjour est déjà clôturé."})

        dt_sortie = date_sortie or timezone.now()
        if dt_sortie < sejour.date_admission:
            raise ValidationError({"date_sortie": "La date de sortie ne peut pas être antérieure à l'admission."})

        sejour.statut = Sejour.StatutSejour.TERMINE
        sejour.date_sortie = dt_sortie
        if motif_sortie:
            sejour.motif_sortie = motif_sortie
        sejour.save(update_fields=["statut", "date_sortie", "motif_sortie", "updated_at"])

        from localisation.models import LocalisationPatient
        from mouvement.models import MouvementPatient
        from evenement.models import EvenementParcours
        from lit.models import Lit

        # Clôturer les localisations actives
        locs_actives = LocalisationPatient.objects.filter(sejour=sejour, est_actuelle=True)
        derniere_loc = None
        for loc in locs_actives:
            loc.est_actuelle = False
            loc.date_fin = dt_sortie
            loc.save(update_fields=["est_actuelle", "date_fin"])
            derniere_loc = loc

            # Si un lit était occupé, le libérer
            if loc.lit_id:
                lit = Lit.objects.select_for_update().get(id=loc.lit_id)
                lit.etat = "DISPONIBLE"
                lit.save(update_fields=["etat"])

        # Mouvement de sortie définitive
        MouvementPatient.objects.create(
            sejour=sejour,
            localisation_origine=derniere_loc,
            localisation_destination=None,
            date_mouvement=dt_sortie,
            type_mouvement=MouvementPatient.TypeMouvement.SORTIE_DEFINITIVE,
            motif=sejour.motif_sortie or "Clôture du séjour",
            enregistre_par=user,
        )

        # Événement de sortie
        EvenementParcours.objects.create(
            sejour=sejour,
            type_evenement=EvenementParcours.TypeEvenement.SORTIE_DEFINITIVE,
            titre="Sortie définitive du patient",
            description=f"Clôture du séjour. Motif: {sejour.motif_sortie or 'Non précisé'}",
            date_evenement=dt_sortie,
            declare_par=user,
            importance=EvenementParcours.NiveauImportance.INFO,
        )

        logger.info(f"Séjour #{sejour.id_sejour} ({sejour.reference}) clôturé avec succès.")
        return sejour

    @transaction.atomic
    def prescrire_analyse(self, sejour_id: int, data: Dict[str, Any], user=None) -> DemandeAnalyse:
        """Prescrit une analyse / examen biologique ou d'imagerie au sein du séjour."""
        sejour = self.repository.get_by_id(sejour_id)
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        from evenement.models import EvenementParcours

        prescripteur_id = data.get("prescripteur_id") or data.get("prescripteur")
        if not prescripteur_id and hasattr(user, "personnel") and hasattr(user.personnel, "medecin"):
            prescripteur_id = user.personnel.medecin.id_medecin

        analyse = DemandeAnalyse.objects.create(
            patient=sejour.patient,
            sejour=sejour,
            prescripteur_id=prescripteur_id,
            type_analyse=data.get("type_analyse", "Examen standard"),
            date_prescription=data.get("date_prescription", timezone.now()),
            commentaire=data.get("commentaire", ""),
            statut=DemandeAnalyse.StatutAnalyse.PRESCRITE,
        )

        EvenementParcours.objects.create(
            sejour=sejour,
            type_evenement=EvenementParcours.TypeEvenement.PRESCRIPTION_EXAMEN,
            titre=f"Prescription examen : {analyse.type_analyse}",
            description=f"Examen prescrit pour le patient. Réf: Analyse #{analyse.id}. {analyse.commentaire or ''}".strip(),
            date_evenement=analyse.date_prescription,
            declare_par=user,
            importance=EvenementParcours.NiveauImportance.INFO,
            donnees_additionnelles={"analyse_id": analyse.id},
        )
        return analyse
