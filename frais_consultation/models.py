from django.db import models


class FraisConsultation(models.Model):

    class StatutPaiement(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente de paiement"
        PAYE = "PAYE", "Payé"
        ANNULE = "ANNULE", "Annulé"

    id = models.AutoField(primary_key=True)

    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Montant des frais de consultation"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description ou détails des prestations incluses"
    )

    date_paiement = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure effectives du règlement"
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutPaiement.choices,
        default=StatutPaiement.EN_ATTENTE
    )

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Frais de Consultation"
        verbose_name_plural = "Frais de Consultations"
        ordering = ['-id']

    def __str__(self):
        return f"Frais #{self.id} - {self.montant} ({self.get_statut_display()})"

    @property
    def idFrais(self) -> int:
        return self.id
