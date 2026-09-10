from django.db import models
from simple_history.models import HistoricalRecords


class LigneOrdonnance(models.Model):
    """
    Modèle structuré représentant une ligne de prescription au sein d'une ordonnance médicale.
    Permet une traçabilité clinique et médico-légale précise des posologies et médicaments.
    """
    id = models.AutoField(primary_key=True)

    ordonnance = models.ForeignKey(
        'ordonnance.Ordonnance',
        on_delete=models.CASCADE,
        related_name='lignes',
        db_column='id_ordonnance',
        help_text="Ordonnance médicale à laquelle cette ligne est rattachée"
    )

    medicament = models.CharField(
        max_length=255,
        help_text="Nom du médicament, DCI ou spécialité (ex: Amoxicilline, Paracétamol)"
    )

    dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Dosage ou concentration (ex: 500 mg, 1 g, 250 mg/5 ml)"
    )

    forme = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Forme pharmaceutique (ex: Comprimé, Gélule, Sirop, Pommade, Injectable)"
    )

    posologie = models.CharField(
        max_length=255,
        help_text="Rythme et modalités d'administration (ex: 1 gélule 3 fois par jour)"
    )

    duree_traitement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Durée de prise prescrite (ex: 5 jours, 10 jours, 1 mois renouvelable)"
    )

    quantite = models.PositiveIntegerField(
        default=1,
        help_text="Quantité prescrite / nombre d'unités ou boîtes"
    )

    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Recommandations cliniques particulières (ex: à prendre pendant les repas)"
    )

    actif = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Ligne d'Ordonnance"
        verbose_name_plural = "Lignes d'Ordonnances"
        ordering = ['id']

    def __str__(self):
        d = f" {self.dosage}" if self.dosage else ""
        return f"{self.medicament}{d} - {self.posologie} ({self.quantite} unité(s))"

    @property
    def idLigne(self) -> int:
        return self.id

    @property
    def id_ligne(self) -> int:
        return self.id
