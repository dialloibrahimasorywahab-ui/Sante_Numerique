# pyrefly: ignore [missing-import]
from django.db import models

class User(models.Model):

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"
        MEDECIN = "MEDECIN", "Medecin"
        INFIRMIER = "INFIRMIER", "Infirmier"

    idUser = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150, blank=False)
    prenom = models.CharField(max_length=150, blank= False)
    email = models.EmailField(max_length=150, unique=True, blank=False)
    telephone = models.CharField(max_length=15, unique=True, blank=False)
    login = models.CharField(max_length=150, unique=True, blank=False)
    motDePasseHash = models.CharField(max_length=255, blank=False)

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    derniereConnexion = models.DateTimeField(
        null=True,
        blank=True
    )
    dateNaissance = models.DateField(
        null=True,
        blank=True
    )
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.login