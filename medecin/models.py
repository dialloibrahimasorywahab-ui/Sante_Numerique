from django.db import models
from users.models import User


class Medecin(models.Model):

    class Specialite(models.TextChoices):
        GENERALISTE = "GENERALISTE", "Médecine Générale"
        CARDIOLOGIE = "CARDIOLOGIE", "Cardiologie"
        PEDIATRIE = "PEDIATRIE", "Pédiatrie"
        GYNECOLOGIE = "GYNECOLOGIE", "Gynécologie"
        NEUROLOGIE = "NEUROLOGIE", "Neurologie"
        DERMATOLOGIE = "DERMATOLOGIE", "Dermatologie"
        CHIRURGIE = "CHIRURGIE", "Chirurgie"
        OPHTALMOLOGIE = "OPHTALMOLOGIE", "Ophtalmologie"
        PSYCHIATRIE = "PSYCHIATRIE", "Psychiatrie"
        RADIOLOGIE = "RADIOLOGIE", "Radiologie"

    idMedecin = models.AutoField(primary_key=True)

    idUtilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="medecin"
    )

    specialite = models.CharField(
        max_length=50,
        choices=Specialite.choices,
        default=Specialite.GENERALISTE
    )

    matricule = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    numeroOrdre = models.CharField(
        max_length=50,
        unique=True
    )

    telephonePro = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    emailPro = models.EmailField(
        blank=True,
        null=True
    )

    bureau = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    dateEmbauche = models.DateField()

    def __str__(self):
        return f"Dr. {self.idUtilisateur.prenom} {self.idUtilisateur.nom} - {self.get_specialite_display()}"
