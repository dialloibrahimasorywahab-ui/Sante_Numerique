# pyrefly: ignore [missing-import]
from django.db import models
from batiment.models import Batiment


class Chambre(models.Model):

    class TypeChambre(models.TextChoices):
        INDIVIDUELLE = "INDIVIDUELLE", "Chambre Individuelle"
        DOUBLE = "DOUBLE", "Chambre Double"
        COMMUNE = "COMMUNE", "Chambre Commune"
        SUITE = "SUITE", "Suite VIP"
        REANIMATION = "REANIMATION", "Soins Intensifs / Réanimation"
        URGENCES = "URGENCES", "Chambre d'Urgences"
        AUTRE = "AUTRE", "Autre"

    class StatutChambre(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        PARTIELLEMENT_OCCUPEE = "PARTIELLEMENT_OCCUPEE", "Partiellement Occupée"
        OCCUPEE = "OCCUPEE", "Occupée / Complète"
        EN_NETTOYAGE = "EN_NETTOYAGE", "En nettoyage / Désinfection"
        HORS_SERVICE = "HORS_SERVICE", "Hors Service / Maintenance"

    id = models.AutoField(primary_key=True)
    batiment = models.ForeignKey(
        Batiment,
        on_delete=models.CASCADE,
        related_name="chambres",
        db_column="id_batiment"
    )
    numero_chambre = models.IntegerField(default=0)
    type_chambre = models.CharField(
        max_length=50,
        choices=TypeChambre.choices,
        default=TypeChambre.INDIVIDUELLE
    )
    capacite = models.PositiveIntegerField(
        default=1,
        help_text="Nombre de lits dans la chambre"
    )
    statut = models.CharField(
        max_length=30,
        choices=StatutChambre.choices,
        default=StatutChambre.DISPONIBLE
    )

    class Meta:
        unique_together = ('batiment', 'numero_chambre')
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"

    def __str__(self):
        return f"Chambre {self.numero_chambre} - {self.batiment.nom} ({self.get_type_chambre_display()}, {self.get_statut_display()})"

    @property
    def idChambre(self) -> int:
        return self.id

    @property
    def lits_disponibles_count(self):
        return self.lits.filter(etat="DISPONIBLE").count()

    @property
    def lits_occupes_count(self):
        return self.lits.filter(etat="OCCUPE").count()

    def sync_statut(self):
        """Calcule et met à jour automatiquement le statut de la chambre selon l'état de ses lits."""
        lits = list(self.lits.all())
        if not lits:
            return self.statut

        nb_dispo = sum(1 for l in lits if l.etat == "DISPONIBLE")
        nb_occupe = sum(1 for l in lits if l.etat == "OCCUPE")
        nb_nettoyage = sum(1 for l in lits if l.etat == "EN_NETTOYAGE")
        nb_hors_service = sum(1 for l in lits if l.etat == "HORS_SERVICE")
        total = len(lits)

        if nb_dispo == total:
            nouveau_statut = self.StatutChambre.DISPONIBLE
        elif nb_occupe == total or (nb_dispo == 0 and nb_occupe > 0):
            nouveau_statut = self.StatutChambre.OCCUPEE
        elif 0 < nb_dispo < total:
            nouveau_statut = self.StatutChambre.PARTIELLEMENT_OCCUPEE
        elif nb_nettoyage == total:
            nouveau_statut = self.StatutChambre.EN_NETTOYAGE
        elif nb_hors_service == total:
            nouveau_statut = self.StatutChambre.HORS_SERVICE
        else:
            nouveau_statut = self.StatutChambre.DISPONIBLE


        if self.statut != nouveau_statut:
            self.statut = nouveau_statut
            self.save(update_fields=["statut"])
        return self.statut


