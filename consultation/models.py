from django.db import models
from django.utils import timezone
from patients.models import Patient
from medecin.models import Medecin
from rendezvous.models import RendezVous
from frais_consultation.models import FraisConsultation


class Consultation(models.Model):

    id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="consultations",
        db_column="id_patient",
        help_text="Patient examiné"
    )

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
        db_column="id_medecin",
        help_text="Médecin consultant"
    )

    rdv = models.ForeignKey(
        RendezVous,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
        db_column="id_rdv",
        help_text="Rendez-vous associé (optionnel)"
    )

    frais = models.ForeignKey(
        FraisConsultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
        db_column="id_frais",
        help_text="Frais de consultation associés (optionnel)"
    )

    date_cons = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure de la consultation"
    )

    symptomes = models.TextField(
        blank=True,
        null=True,
        help_text="Symptômes rapportés par le patient"
    )

    diagnostic = models.TextField(
        blank=True,
        null=True,
        help_text="Diagnostic médical établi"
    )

    observations = models.TextField(
        blank=True,
        null=True,
        help_text="Observations ou conseils de suivi"
    )

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = ['-date_cons', '-id']

    def __str__(self):
        pat_nom = f"{self.patient.idUtilisateur.prenom} {self.patient.idUtilisateur.nom}" if self.patient and self.patient.idUtilisateur else f"Patient #{self.patient_id}"
        med_nom = f"Dr. {self.medecin.idUtilisateur.prenom} {self.medecin.idUtilisateur.nom}" if self.medecin and self.medecin.idUtilisateur else f"Médecin #{self.medecin_id}"
        return f"Consultation #{self.id} - {pat_nom} avec {med_nom} le {self.date_cons.strftime('%Y-%m-%d %H:%M')}"

    @property
    def idConsultation(self) -> int:
        return self.id
