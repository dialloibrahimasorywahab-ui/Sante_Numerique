from django.db import models
from patients.models import Patient
from medecin.models import Medecin


class Natalite(models.Model):

    class Sexe(models.TextChoices):
        MASCULIN = "M", "Masculin"
        FEMININ = "F", "Féminin"

    class GroupeSanguin(models.TextChoices):
        A_POSITIF = "A+", "A+"
        A_NEGATIF = "A-", "A-"
        B_POSITIF = "B+", "B+"
        B_NEGATIF = "B-", "B-"
        AB_POSITIF = "AB+", "AB+"
        AB_NEGATIF = "AB-", "AB-"
        O_POSITIF = "O+", "O+"
        O_NEGATIF = "O-", "O-"

    id_nouveau_ne = models.AutoField(primary_key=True)

    id_patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="natalites",
        db_column="id_patient",
        help_text="Patient représentant la mère / le parent"
    )

    id_medecin = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="naissances_supervisees",
        db_column="id_medecin",
        help_text="Médecin superviseur ou accoucheur"
    )

    prenom_nouveau_ne = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    nom_nouveau_ne = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    date_naissance = models.DateField(
        null=False,
        blank=False
    )

    heure_naissance = models.TimeField(
        null=True,
        blank=True
    )

    sexe = models.CharField(
        max_length=1,
        choices=Sexe.choices
    )

    groupe_sanguin = models.CharField(
        max_length=10,
        choices=GroupeSanguin.choices,
        blank=True,
        null=True
    )

    poids = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Poids en kg (ex: 3.25)"
    )

    taille = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taille en cm (ex: 50.0)"
    )

    lieu_naissance = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    observation = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Natalité"
        verbose_name_plural = "Natalités"
        ordering = ['-date_naissance', '-id_nouveau_ne']

    def __str__(self):
        nom_bebe = f"{self.prenom_nouveau_ne or ''} {self.nom_nouveau_ne or ''}".strip()
        label = nom_bebe if nom_bebe else f"Nouveau-né #{self.id_nouveau_ne}"
        return f"{label} (Né(e) le {self.date_naissance})"

    @property
    def idNouveauNe(self):
        return self.id_nouveau_ne