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

    id_medecin = models.AutoField(primary_key=True)

    id_utilisateur = models.OneToOneField(
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

    numero_ordre = models.CharField(
        max_length=50,
        unique=True
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

    bureau = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    date_embauche = models.DateField()

    class Meta:
        ordering = ["id_medecin"]

    # Propriétés de compatibilité camelCase
    @property
    def idMedecin(self):
        return self.id_medecin

    @idMedecin.setter
    def idMedecin(self, val):
        self.id_medecin = val

    @property
    def idUtilisateur(self):
        return self.id_utilisateur

    @idUtilisateur.setter
    def idUtilisateur(self, val):
        self.id_utilisateur = val

    @property
    def numeroOrdre(self):
        return self.numero_ordre

    @numeroOrdre.setter
    def numeroOrdre(self, val):
        self.numero_ordre = val

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
        return f"Dr. {self.id_utilisateur.prenom} {self.id_utilisateur.nom} - {self.get_specialite_display()}"
