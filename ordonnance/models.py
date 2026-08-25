# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.utils import timezone
# pyrefly: ignore [missing-import]
from consultation.models import Consultation


class Ordonnance(models.Model):

    id = models.AutoField(primary_key=True)

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="ordonnances",
        db_column="id_consultation",
        help_text="Consultation ayant donné lieu à la prescription"
    )

    reference = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Numéro ou référence unique de l'ordonnance (ex: ORD-20260825-001)"
    )

    date_ordonnance = models.DateField(
        default=timezone.now,
        help_text="Date de la prescription"
    )

    observation = models.TextField(
        blank=True,
        null=True,
        help_text="Détail des médicaments, dosages et posologies"
    )

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ordonnance"
        verbose_name_plural = "Ordonnances"
        ordering = ['-date_ordonnance', '-id']

    def __str__(self):
        ref = self.reference or f"#{self.id}"
        return f"Ordonnance {ref} - Consultation #{self.consultation_id} ({self.date_ordonnance})"

    @property
    def idOrdonnance(self) -> int:
        return self.id
