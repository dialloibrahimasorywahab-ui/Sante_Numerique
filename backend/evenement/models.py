from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class EvenementParcours(models.Model):
    """
    Timeline clinique et administrative d'un séjour patient.
    Conserve chaque événement marquant avec horodatage immuable et métadonnées extensibles.
    """

    class TypeEvenement(models.TextChoices):
        ADMISSION = "ADMISSION", "Admission du patient"
        CONSULTATION = "CONSULTATION", "Consultation médicale / urgences"
        PRESCRIPTION_EXAMEN = "PRESCRIPTION_EXAMEN", "Prescription d'un examen / analyse"
        EXAMEN_EN_COURS = "EXAMEN_EN_COURS", "Examen en cours au laboratoire / imagerie"
        RESULTAT_EXAMEN = "RESULTAT_EXAMEN", "Résultats d'examen disponibles"
        TRANSFERT_INTERNE = "TRANSFERT_INTERNE", "Transfert interne"
        ATTRIBUTION_LIT = "ATTRIBUTION_LIT", "Attribution d'un lit d'hospitalisation"
        LIBERATION_LIT = "LIBERATION_LIT", "Libération d'un lit"
        SOIN_ADMINISTRE = "SOIN_ADMINISTRE", "Administration d'un soin / traitement"
        OBSERVATION = "OBSERVATION", "Observation clinique / note de relève"
        SORTIE_AUTORISEE = "SORTIE_AUTORISEE", "Validation médicale de la sortie"
        SORTIE_DEFINITIVE = "SORTIE_DEFINITIVE", "Sortie effective de l'établissement"
        AUTRE = "AUTRE", "Autre événement"

    class NiveauImportance(models.TextChoices):
        INFO = "INFO", "Information standard"
        ATTENTION = "ATTENTION", "Attention requise / Vigilance"
        CRITIQUE = "CRITIQUE", "Critique / Urgence médicale"

    id = models.AutoField(primary_key=True)

    sejour = models.ForeignKey(
        "sejour.Sejour",
        on_delete=models.CASCADE,
        related_name="evenements",
        help_text="Séjour auquel cet événement est rattaché"
    )

    type_evenement = models.CharField(
        max_length=40,
        choices=TypeEvenement.choices,
        default=TypeEvenement.OBSERVATION,
        db_index=True,
        help_text="Catégorie normalisée de l'événement"
    )

    titre = models.CharField(
        max_length=200,
        help_text="Intitulé concis de l'événement"
    )

    description = models.TextField(
        blank=True,
        default="",
        help_text="Détails circonstanciés ou compte-rendu textuel"
    )

    date_evenement = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Horodatage clinique de l'événement"
    )

    declare_par = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evenements_declares",
        help_text="Agent ou praticien ayant enregistré l'événement"
    )

    importance = models.CharField(
        max_length=20,
        choices=NiveauImportance.choices,
        default=NiveauImportance.INFO,
        help_text="Degré de priorité ou criticité de l'événement"
    )

    donnees_additionnelles = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées structurées contextuelles (ex: constantes vitales, identifiants)"
    )

    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Événement du Parcours"
        verbose_name_plural = "Événements du Parcours"
        ordering = ["-date_evenement", "-id"]

    def __str__(self):
        ref = self.sejour.reference if self.sejour_id else "Séjour inconnu"
        return f"[{self.importance}] {ref} - {self.titre} ({self.date_evenement.strftime('%d/%m/%Y %H:%M')})"
