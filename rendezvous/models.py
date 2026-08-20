# pyrefly: ignore [missing-import]
from django.db import models
from patients.models import Patient
from medecin.models import Medecin


class RendezVous(models.Model):

    class StatutRendezVous(models.TextChoices):
        PROGRAMME = "PROGRAMME", "Programmé"
        CONFIRME = "CONFIRME", "Confirmé"
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        EN_COURS = "EN_COURS", "En cours de consultation"
        TERMINE = "TERMINE", "Terminé"
        ANNULE = "ANNULE", "Annulé"
        ABSENT = "ABSENT", "Absent / Non honoré"

    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="rendezvous",
        db_column="id_patient"
    )
    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="rendezvous",
        db_column="id_medecin"
    )
    date_rdv = models.DateField()
    heure = models.TimeField()
    motif = models.TextField(blank=True, null=True)
    statut = models.CharField(
        max_length=30,
        choices=StatutRendezVous.choices,
        default=StatutRendezVous.EN_ATTENTE
    )


    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-date_rdv', '-heure']

    def __str__(self):
        pat_nom = f"{self.patient.idUtilisateur.prenom} {self.patient.idUtilisateur.nom}" if self.patient and self.patient.idUtilisateur else f"Patient #{self.patient_id}"
        med_nom = f"Dr. {self.medecin.idUtilisateur.prenom} {self.medecin.idUtilisateur.nom}" if self.medecin and self.medecin.idUtilisateur else f"Médecin #{self.medecin_id}"
        return f"RDV #{self.id} - {pat_nom} avec {med_nom} le {self.date_rdv} à {self.heure} ({self.get_statut_display()})"

    @property
    def idRendezVous(self):
        return self.id
