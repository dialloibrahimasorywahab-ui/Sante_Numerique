# pyrefly: ignore [missing-import]
from django.db import models


class Batiment(models.Model):
    idBatiment = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    nombre_chambre = models.PositiveIntegerField(null=True, blank=True, default=None)
    actif = models.BooleanField(default=True)

    def __str__(self):
        if self.nombre_chambre is not None:
            return f"{self.nom} ({self.nombre_chambre} chambres)"
        return self.nom

    @property
    def total_chambres_effectif(self):
        count = self.chambres.count()
        if count > 0:
            return count
        return self.nombre_chambre

    def sync_nombre_chambres(self):
        self.nombre_chambre = self.chambres.count()
        self.save(update_fields=["nombre_chambre"])
        return self.nombre_chambre

