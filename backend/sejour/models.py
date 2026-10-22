from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Sejour(models.Model):
    """
    Représente la prise en charge continue d'un patient dans l'établissement hospitalier,
    depuis son admission jusqu'à sa sortie définitive.
    """

    class TypePriseEnCharge(models.TextChoices):
        URGENCE = "URGENCE", "Urgences"
        CONSULTATION = "CONSULTATION", "Consultation externe"
        HOSPITALISATION_PROGRAMMEE = "HOSPITALISATION_PROGRAMMEE", "Hospitalisation programmée"
        TRANSFERT_EXTERNE = "TRANSFERT_EXTERNE", "Transfert depuis un autre établissement"
        AUTRE = "AUTRE", "Autre prise en charge"

    class StatutSejour(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente de prise en charge"
        EN_COURS = "EN_COURS", "En cours de soins"
        TRANSFERE = "TRANSFERE", "Transféré (en cours)"
        SORTIE_AUTORISEE = "SORTIE_AUTORISEE", "Sortie autorisée"
        TERMINE = "TERMINE", "Terminé (Sortie effectuée)"
        ANNULE = "ANNULE", "Annulé"

    id_sejour = models.AutoField(primary_key=True)
    reference = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Référence unique et lisible du séjour (ex: S-2026-0001)"
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="sejours",
        help_text="Dossier patient associé"
    )

    service_responsable = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="sejours",
        help_text="Service hospitalier actuellement responsable du patient"
    )

    medecin_responsable = models.ForeignKey(
        "medecin.Medecin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sejours_responsable",
        help_text="Praticien référent / responsable du séjour"
    )

    enregistre_par = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sejours_enregistres",
        help_text="Utilisateur ayant enregistré l'admission"
    )

    type_prise_en_charge = models.CharField(
        max_length=40,
        choices=TypePriseEnCharge.choices,
        default=TypePriseEnCharge.URGENCE,
        help_text="Type initial de prise en charge"
    )

    statut = models.CharField(
        max_length=30,
        choices=StatutSejour.choices,
        default=StatutSejour.EN_COURS,
        help_text="Cycle de vie du séjour"
    )

    date_admission = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure de l'admission"
    )

    motif_admission = models.TextField(
        help_text="Motif médical ou administratif de l'admission"
    )

    date_sortie = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure de sortie définitive"
    )

    motif_sortie = models.TextField(
        null=True,
        blank=True,
        help_text="Motif / compte-rendu de sortie"
    )

    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Séjour Hospitalier"
        verbose_name_plural = "Séjours Hospitaliers"
        ordering = ["-date_admission", "-id_sejour"]

    def __str__(self):
        nom_patient = str(self.patient) if self.patient else "Patient Inconnu"
        return f"{self.reference} - {nom_patient} ({self.get_statut_display()})"

    @property
    def id(self) -> int:
        return self.id_sejour

    @property
    def idSejour(self) -> int:
        return self.id_sejour

    @property
    def is_active(self) -> bool:
        return self.actif and self.statut in [
            self.StatutSejour.EN_ATTENTE,
            self.StatutSejour.EN_COURS,
            self.StatutSejour.TRANSFERE,
            self.StatutSejour.SORTIE_AUTORISEE,
        ]

    @property
    def localisation_actuelle(self):
        """Retourne la localisation actuellement active du patient."""
        if hasattr(self, 'localisations'):
            return self.localisations.filter(est_actuelle=True).first()
        return None

    def clean(self):
        super().clean()
        if self.date_admission and self.date_sortie and self.date_sortie < self.date_admission:
            raise ValidationError({
                "date_sortie": "La date de sortie ne peut pas être antérieure à la date d'admission."
            })

    @classmethod
    def generer_nouvelle_reference(cls) -> str:
        """Génère une référence unique au format S-YYYY-XXXX."""
        annee = timezone.now().year
        prefixe = f"S-{annee}-"
        dernier_sejour = cls.objects.filter(reference__startswith=prefixe).order_by("-reference").first()
        if dernier_sejour and len(dernier_sejour.reference.split("-")) == 3:
            try:
                dernier_num = int(dernier_sejour.reference.split("-")[2])
                nouveau_num = dernier_num + 1
            except ValueError:
                nouveau_num = 1
        else:
            nouveau_num = 1
        nouvelle_ref = f"{prefixe}{nouveau_num:04d}"
        while cls.objects.filter(reference=nouvelle_ref).exists():
            nouveau_num += 1
            nouvelle_ref = f"{prefixe}{nouveau_num:04d}"
        return nouvelle_ref


class DemandeAnalyse(models.Model):
    """
    Structure minimale pour les examens biologiques (laboratoire) ou d'imagerie médicale.
    """

    class StatutAnalyse(models.TextChoices):
        PRESCRITE = "PRESCRITE", "Prescrite"
        PRELEVEE = "PRELEVEE", "Prélèvement effectué"
        EN_COURS = "EN_COURS", "Analyse en cours au laboratoire"
        TERMINEE = "TERMINEE", "Résultats disponibles"
        ANNULEE = "ANNULEE", "Annulée"

    id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="demandes_analyses"
    )

    sejour = models.ForeignKey(
        Sejour,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes_analyses"
    )

    prescripteur = models.ForeignKey(
        "medecin.Medecin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyses_prescrites"
    )

    type_analyse = models.CharField(
        max_length=150,
        help_text="Ex: NFS (Numération Formule Sanguine), Ionogramme, Radiographie Thorax"
    )

    date_prescription = models.DateTimeField(default=timezone.now)
    statut = models.CharField(
        max_length=30,
        choices=StatutAnalyse.choices,
        default=StatutAnalyse.PRESCRITE
    )

    date_prelevement = models.DateTimeField(null=True, blank=True)
    date_resultat = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Demande d'Analyse"
        verbose_name_plural = "Demandes d'Analyses"
        ordering = ["-date_prescription", "-id"]

    def __str__(self):
        return f"Analyse #{self.id} - {self.type_analyse} ({self.get_statut_display()})"
