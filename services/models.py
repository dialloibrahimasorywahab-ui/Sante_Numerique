from django.db import models


class Service(models.Model):

    class NomService(models.TextChoices):
        MEDECINE_GENERALE = "MEDECINE_GENERALE", "Médecine Générale"
        URGENCES = "URGENCES", "Urgences & Soignants"
        CARDIOLOGIE = "CARDIOLOGIE", "Cardiologie"
        PEDIATRIE = "PEDIATRIE", "Pédiatrie"
        GYNECOLOGIE = "GYNECOLOGIE", "Gynécologie"
        NEUROLOGIE = "NEUROLOGIE", "Neurologie"
        DERMATOLOGIE = "DERMATOLOGIE", "Dermatologie"
        CHIRURGIE = "CHIRURGIE", "Chirurgie Générale"
        OPHTALMOLOGIE = "OPHTALMOLOGIE", "Ophtalmologie"
        PSYCHIATRIE = "PSYCHIATRIE", "Psychiatrie"
        RADIOLOGIE = "RADIOLOGIE", "Radiologie & Imagerie Médicale"
        LABORATOIRE = "LABORATOIRE", "Laboratoire & Analyses"
        PHARMACIE = "PHARMACIE", "Pharmacie Centrale"
        MATERNITE = "MATERNITE", "Maternité"
        ADMINISTRATION = "ADMINISTRATION", "Administration & Accueil"
        REANIMATION = "REANIMATION", "Réanimation"
        AUTRE = "AUTRE", "Autre Service"

    idService = models.AutoField(primary_key=True)

    nomService = models.CharField(
        max_length=100,
        choices=NomService.choices,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    bureauLocalisation = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.get_nomService_display()
