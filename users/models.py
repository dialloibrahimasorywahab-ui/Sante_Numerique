from django.db import models

class User(models.Model):

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"
        MEDECIN = "MEDECIN", "Medecin"
        INFIRMIER = "INFIRMIER", "Infirmier"

    idUser = models.AutoField(primary_key=True)
    login = models.CharField(max_length=150, unique=True)
    motDePasseHash = models.CharField(max_length=120)

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    derniereConnexion = models.DateTimeField(
        null=True,
        blank=True
    )
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.login