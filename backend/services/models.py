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

    id_service = models.AutoField(primary_key=True)

    nom_service = models.CharField(
        max_length=100,
        choices=NomService.choices,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    bureau_localisation = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['id_service']

    # Propriétés de compatibilité camelCase
    @property
    def idService(self):
        return self.id_service

    @idService.setter
    def idService(self, val):
        self.id_service = val

    @property
    def nomService(self):
        return self.nom_service

    @nomService.setter
    def nomService(self, val):
        self.nom_service = val

    @property
    def bureauLocalisation(self):
        return self.bureau_localisation

    @bureauLocalisation.setter
    def bureauLocalisation(self, val):
        self.bureau_localisation = val

    def __str__(self):
        return self.get_nom_service_display()
