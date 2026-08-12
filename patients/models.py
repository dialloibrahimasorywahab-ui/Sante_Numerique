from django.db import models
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

    idPatient = models.AutoField(primary_key=True)

    idUtilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient"
    )

    nom = models.CharField(max_length=100)

    prenom = models.CharField(max_length=100)

    dateNaissance = models.DateField()

    sexe = models.CharField(
        max_length=1,
        choices=Sexe.choices
    )

    adresse = models.CharField(max_length=255)

    telephone = models.CharField(max_length=20)

    email = models.EmailField()

    groupeSanguin = models.CharField(
        max_length=3,
        choices=GroupeSanguin.choices
    )

    numeroSecuriteSociale = models.CharField(
        max_length=50
    )

    personneAContacter = models.CharField(
        max_length=100
    )

    dateInscription = models.DateField()

    def __str__(self):
        return f"{self.prenom} {self.nom}"
