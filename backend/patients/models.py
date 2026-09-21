from django.db import models
from simple_history.models import HistoricalRecords
from users.models import User



class Patient(models.Model):

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

    id_patient = models.AutoField(primary_key=True)

    id_utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient"
    )

    date_naissance = models.DateField(
        null=True,
        blank=True
    )

    sexe = models.CharField(
        max_length=1,
        choices=Sexe.choices
    )

    adresse = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    groupe_sanguin = models.CharField(
        max_length=3,
        choices=GroupeSanguin.choices
    )

    numero_securite_sociale = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    personne_a_contacter = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    date_inscription = models.DateField()

    id_medecin = models.ForeignKey(
        "medecin.Medecin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients",
        db_column="id_medecin",
        help_text="Médecin ayant enregistré ce patient"
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ['id_patient']

    @property
    def id(self):
        return self.id_patient

    def __str__(self):
        return f"Patient: {self.id_utilisateur.prenom} {self.id_utilisateur.nom}"
