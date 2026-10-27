import logging
from typing import Any, Dict, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import LocalisationPatient
from .localisationRepositories import LocalisationRepository

logger = logging.getLogger(__name__)


class LocalisationService:
    """Service gérant les affectations physiques et la gestion des lits."""

    def __init__(self):
        self.repository = LocalisationRepository()

    @transaction.atomic
    def affecter_localisation(
        self,
        sejour_id: int,
        data: Dict[str, Any],
        user=None,
    ) -> LocalisationPatient:
        """
        Affecte le patient à un nouvel emplacement physique (ex: lit d'hospitalisation, box, brancard).
        - Clôture l'ancienne localisation active.
        - Verrouille et vérifie la disponibilité du nouveau lit (si précisé).
        - Libère l'ancien lit si un lit était précédemment occupé.
        - Crée la nouvelle localisation active.
        """
        from sejour.models import Sejour
        from lit.models import Lit

        sejour = Sejour.objects.filter(id_sejour=sejour_id).first()
        if not sejour:
            raise ValidationError({"sejour": "Séjour introuvable."})

        if sejour.statut in [Sejour.StatutSejour.TERMINE, Sejour.StatutSejour.ANNULE]:
            raise ValidationError({"sejour": "Impossible d'affecter une localisation à un séjour clos ou annulé."})

        service_id = data.get("service_id") or data.get("service") or sejour.service_responsable_id
        batiment_id = data.get("batiment_id") or data.get("batiment")
        chambre_id = data.get("chambre_id") or data.get("chambre")
        lit_id = data.get("lit_id") or data.get("lit")
        date_debut = data.get("date_debut") or timezone.now()
        motif = data.get("motif", "")
        commentaire = data.get("commentaire", "")

        # Verrouiller le nouveau lit si sélectionné
        if lit_id:
            nouveau_lit = Lit.objects.select_for_update().filter(id=lit_id).first()
            if not nouveau_lit:
                raise ValidationError({"lit": f"Lit #{lit_id} introuvable."})
            if nouveau_lit.etat != "DISPONIBLE":
                raise ValidationError({"lit": f"Le lit #{nouveau_lit.numero_lit or nouveau_lit.id} n'est pas disponible ({nouveau_lit.etat})."})
            
            nouveau_lit.etat = "OCCUPE"
            nouveau_lit.save(update_fields=["etat"])
            if nouveau_lit.chambre:
                nouveau_lit.chambre.sync_statut()

            if not chambre_id:
                chambre_id = nouveau_lit.chambre_id
            if chambre_id and not batiment_id:
                batiment_id = nouveau_lit.chambre.batiment_id

        # Clôturer l'ancienne localisation
        ancienne_loc = LocalisationPatient.objects.filter(sejour=sejour, est_actuelle=True).first()
        if ancienne_loc:
            ancienne_loc.est_actuelle = False
            ancienne_loc.date_fin = date_debut
            ancienne_loc.save(update_fields=["est_actuelle", "date_fin"])

            # Libérer l'ancien lit s'il était différent
            if ancienne_loc.lit_id and ancienne_loc.lit_id != lit_id:
                ancien_lit = Lit.objects.select_for_update().filter(id=ancienne_loc.lit_id).first()
                if ancien_lit:
                    ancien_lit.etat = "DISPONIBLE"
                    ancien_lit.save(update_fields=["etat"])
                    if ancien_lit.chambre:
                        ancien_lit.chambre.sync_statut()

        nouvelle_loc = LocalisationPatient(
            sejour=sejour,
            service_id=service_id,
            batiment_id=batiment_id,
            chambre_id=chambre_id,
            lit_id=lit_id,
            date_debut=date_debut,
            est_actuelle=True,
            motif=motif,
            commentaire=commentaire,
            enregistre_par=user,
        )
        nouvelle_loc.full_clean()
        nouvelle_loc.save()

        logger.info(f"Localisation mise à jour pour le séjour #{sejour.reference} -> Loc #{nouvelle_loc.id}")
        return nouvelle_loc
