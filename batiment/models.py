# pyrefly: ignore [missing-import]
from django.db import models


class Batiment(models.Model):
    idBatiment = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    nombre_chambre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} ({self.nombre_chambre} chambres)"

    @property
    def total_chambres_effectif(self):
        return self.chambres.count()

    def sync_nombre_chambres(self):
        self.nombre_chambre = self.chambres.count()
        self.save(update_fields=["nombre_chambre"])
        return self.nombre_chambre

