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

    id_personnel = models.AutoField(primary_key=True)

    id_utilisateur = models.OneToOneField(
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

    type_personnel = models.CharField(
        max_length=50,
        choices=TypePersonnel.choices,
        default=TypePersonnel.INFIRMIER
    )

    poste = models.CharField(
        max_length=100,
        default="Personnel Soignant"
    )

    id_service = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personnels"
    )

    service_hopital = models.CharField(
        max_length=100,
        default="Médecine Générale"
    )

    telephone_pro = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email_pro = models.EmailField(
        blank=True,
        null=True
    )

    date_embauche = models.DateField()

    class Meta:
        ordering = ['id_personnel']

    # Propriétés de compatibilité camelCase
    @property
    def idPersonnel(self):
        return self.id_personnel

    @idPersonnel.setter
    def idPersonnel(self, val):
        self.id_personnel = val

    @property
    def idUtilisateur(self):
        return self.id_utilisateur

    @idUtilisateur.setter
    def idUtilisateur(self, val):
        self.id_utilisateur = val

    @property
    def typePersonnel(self):
        return self.type_personnel

    @typePersonnel.setter
    def typePersonnel(self, val):
        self.type_personnel = val

    @property
    def idService(self):
        return self.id_service

    @idService.setter
    def idService(self, val):
        self.id_service = val

    @property
    def serviceHopital(self):
        return self.service_hopital

    @serviceHopital.setter
    def serviceHopital(self, val):
        self.service_hopital = val

    @property
    def telephonePro(self):
        return self.telephone_pro

    @telephonePro.setter
    def telephonePro(self, val):
        self.telephone_pro = val

    @property
    def emailPro(self):
        return self.email_pro

    @emailPro.setter
    def emailPro(self, val):
        self.email_pro = val

    @property
    def dateEmbauche(self):
        return self.date_embauche

    @dateEmbauche.setter
    def dateEmbauche(self, val):
        self.date_embauche = val

    def __str__(self):
        return f"{self.get_type_personnel_display()} - {self.id_utilisateur.prenom} {self.id_utilisateur.nom}"
