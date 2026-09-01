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

    id_patient = models.AutoField(primary_key=True)

    id_utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient"
    )

    date_naissance = models.DateField(
        null=True,
        blank=True
    )

    sexe = models.CharField(
        max_length=1,
        choices=Sexe.choices
    )

    adresse = models.CharField(max_length=255)

    groupe_sanguin = models.CharField(
        max_length=3,
        choices=GroupeSanguin.choices
    )

    numero_securite_sociale = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    personne_a_contacter = models.CharField(
        max_length=100
    )

    date_inscription = models.DateField()

    class Meta:
        ordering = ['id_patient']

    # Propriétés de compatibilité camelCase
    @property
    def idPatient(self):
        return self.id_patient

    @idPatient.setter
    def idPatient(self, val):
        self.id_patient = val

    @property
    def idUtilisateur(self):
        return self.id_utilisateur

    @idUtilisateur.setter
    def idUtilisateur(self, val):
        self.id_utilisateur = val

    @property
    def dateNaissance(self):
        return self.date_naissance

    @dateNaissance.setter
    def dateNaissance(self, val):
        self.date_naissance = val

    @property
    def groupeSanguin(self):
        return self.groupe_sanguin

    @groupeSanguin.setter
    def groupeSanguin(self, val):
        self.groupe_sanguin = val

    @property
    def numeroSecuriteSociale(self):
        return self.numero_securite_sociale

    @numeroSecuriteSociale.setter
    def numeroSecuriteSociale(self, val):
        self.numero_securite_sociale = val

    @property
    def personneAContacter(self):
        return self.personne_a_contacter

    @personneAContacter.setter
    def personneAContacter(self, val):
        self.personne_a_contacter = val

    @property
    def dateInscription(self):
        return self.date_inscription

    @dateInscription.setter
    def dateInscription(self, val):
        self.date_inscription = val

    def __str__(self):
        return f"Patient: {self.id_utilisateur.prenom} {self.id_utilisateur.nom}"
