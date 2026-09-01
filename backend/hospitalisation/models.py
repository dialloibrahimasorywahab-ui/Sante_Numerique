from django.db import models
from django.utils import timezone
from patients.models import Patient
from medecin.models import Medecin
from lit.models import Lit


class Hospitalisation(models.Model):

    class StatutHospitalisation(models.TextChoices):
        PROGRAMMEE = "PROGRAMMEE", "Programmée"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée (Sortie)"
        ANNULEE = "ANNULEE", "Annulée"

    id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="hospitalisations",
        db_column="id_patient",
        help_text="Patient hospitalisé"
    )

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hospitalisations",
        db_column="id_medecin",
        help_text="Médecin traitant / responsable"
    )

    lit = models.ForeignKey(
        Lit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hospitalisations",
        db_column="id_lit",
        help_text="Lit attribué au patient"
    )

    date_entree = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure d'admission / d'entrée"
    )

    date_sortie = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure de sortie de l'hôpital"
    )

    motif = models.TextField(
        blank=True,
        null=True,
        help_text="Motif de l'hospitalisation"
    )

    statut = models.CharField(
        max_length=30,
        choices=StatutHospitalisation.choices,
        default=StatutHospitalisation.EN_COURS
    )

    observation = models.TextField(
        blank=True,
        null=True,
        help_text="Observations médicales ou notes de suivi"
    )

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hospitalisation"
        verbose_name_plural = "Hospitalisations"
        ordering = ['-date_entree', '-id']

    def __str__(self):
        patient_nom = f"{self.patient.idUtilisateur.prenom} {self.patient.idUtilisateur.nom}" if self.patient and self.patient.idUtilisateur else f"Patient #{self.patient_id}"
        return f"Hospitalisation #{self.id} - {patient_nom} ({self.get_statut_display()})"

    @property
    def idHospitalisation(self) -> int:
        return self.id
