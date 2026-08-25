# pyrefly: ignore [missing-import]
from django.db import models
from chambre.models import Chambre


class Lit(models.Model):

    class EtatLit(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        OCCUPE = "OCCUPE", "Occupé"
        RESERVE = "RESERVE", "Réservé"
        EN_NETTOYAGE = "EN_NETTOYAGE", "En nettoyage / Désinfection"
        HORS_SERVICE = "HORS_SERVICE", "Hors service / Maintenance"

    id = models.AutoField(primary_key=True)
    chambre = models.ForeignKey(
        Chambre,
        on_delete=models.CASCADE,
        related_name="lits",
        db_column="id_chambre"
    )
    numero_lit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Identifiant ou numéro du lit (ex: Lit A, Lit 1, L-101-1)"
    )
    etat = models.CharField(
        max_length=30,
        choices=EtatLit.choices,
        default=EtatLit.DISPONIBLE
    )

    class Meta:
        verbose_name = "Lit"
        verbose_name_plural = "Lits"
        unique_together = ('chambre', 'numero_lit')
        ordering = ["chambre", "id"]


    def __str__(self):
        label_lit = f" {self.numero_lit}" if self.numero_lit else f" #{self.id}"
        return f"Lit{label_lit} - {self.chambre.batiment.nom} / Chambre {self.chambre.numero_chambre} ({self.get_etat_display()})"

    @property
    def idLit(self) -> int:
        return self.id
