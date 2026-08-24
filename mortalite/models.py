from django.db import models
from patients.models import Patient
from medecin.models import Medecin


class Mortalite(models.Model):
    id_deces = models.AutoField(primary_key=True)

    id_patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="mortalites",
        db_column="id_patient"
    )

    id_medecin = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deces_constates",
        db_column="id_medecin",
        help_text="Médecin ayant constaté le décès"
    )

    date_deces = models.DateField()
    heure_deces = models.TimeField(null=True, blank=True)
    cause_deces = models.TextField(help_text="Cause principale ou diagnostiquée du décès")
    lieu_deces = models.CharField(max_length=255, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Mortalité"
        verbose_name_plural = "Mortalités"
        ordering = ['-date_deces', '-id_deces']

    def __str__(self):
        patient_nom = f"{self.id_patient.idUtilisateur.prenom} {self.id_patient.idUtilisateur.nom}" if self.id_patient and self.id_patient.idUtilisateur else f"Patient #{self.id_patient_id}"
        return f"Décès #{self.id_deces} - {patient_nom} le {self.date_deces}"

    @property
    def idDeces(self):
        return self.id_deces
