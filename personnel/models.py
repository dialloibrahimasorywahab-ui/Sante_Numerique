from django.db import models
from users.models import User


class Personnel(models.Model):

    class TypePersonnel(models.TextChoices):
        INFIRMIER = "INFIRMIER", "Infirmier(e)"
        ADMINISTRATIF = "ADMINISTRATIF", "Personnel Administratif"
        TECHNICIEN = "TECHNICIEN", "Technicien de Laboratoire / Radiologie"
        PHARMACIEN = "PHARMACIEN", "Pharmacien(ne)"
        SAGE_FEMME = "SAGE_FEMME", "Sage-Femme"
        AUTRE = "AUTRE", "Autre Personnel"

    idPersonnel = models.AutoField(primary_key=True)

    idUtilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="personnel"
    )

    matricule = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    typePersonnel = models.CharField(
        max_length=50,
        choices=TypePersonnel.choices,
        default=TypePersonnel.INFIRMIER
    )

    poste = models.CharField(
        max_length=100,
        default="Personnel Soignant"
    )

    idService = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personnels"
    )

    serviceHopital = models.CharField(
        max_length=100,
        default="Médecine Générale"
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

    dateEmbauche = models.DateField()

    class Meta:
        ordering = ['idPersonnel']

    def __str__(self):
        return f"{self.get_typePersonnel_display()} - {self.idUtilisateur.prenom} {self.idUtilisateur.nom}"
