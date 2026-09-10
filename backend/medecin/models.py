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

    @property
    def id(self):
        return self.id_medecin

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


class DisponibiliteMedecin(models.Model):
    """
    Créneaux de disponibilité réguliers du médecin par jour de la semaine.
    Permet au médecin de définir ses plages de travail habituelles.
    """
    class JourSemaine(models.IntegerChoices):
        LUNDI = 0, "Lundi"
        MARDI = 1, "Mardi"
        MERCREDI = 2, "Mercredi"
        JEUDI = 3, "Jeudi"
        VENDREDI = 4, "Vendredi"
        SAMEDI = 5, "Samedi"
        DIMANCHE = 6, "Dimanche"

    id = models.AutoField(primary_key=True)
    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="disponibilites",
        db_column="id_medecin"
    )
    jour_semaine = models.IntegerField(
        choices=JourSemaine.choices,
        help_text="Jour de la semaine (0=Lundi, ..., 6=Dimanche)"
    )
    heure_debut = models.TimeField(
        default="08:30",
        help_text="Heure de début de consultation"
    )
    heure_fin = models.TimeField(
        default="16:30",
        help_text="Heure de fin de consultation"
    )
    pause_debut = models.TimeField(
        null=True,
        blank=True,
        default="12:30",
        help_text="Début de la pause déjeuner (optionnel)"
    )
    pause_fin = models.TimeField(
        null=True,
        blank=True,
        default="14:00",
        help_text="Fin de la pause déjeuner (optionnel)"
    )
    duree_creneau = models.IntegerField(
        default=45,
        help_text="Durée moyenne d'une consultation en minutes"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Indique si le médecin consulte ce jour-là"
    )

    class Meta:
        verbose_name = "Disponibilité Médecin"
        verbose_name_plural = "Disponibilités Médecins"
        unique_together = ("medecin", "jour_semaine")
        ordering = ["jour_semaine", "heure_debut"]

    def __str__(self):
        return f"{self.medecin} - {self.get_jour_semaine_display()} ({self.heure_debut} - {self.heure_fin})"


class IndisponibiliteMedecin(models.Model):
    """
    Périodes d'indisponibilité, congés, formations ou absences exceptionnelles du médecin.
    Bloque automatiquement les créneaux concernés lors de la prise de rendez-vous.
    """
    id = models.AutoField(primary_key=True)
    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="indisponibilites",
        db_column="id_medecin"
    )
    date_debut = models.DateField(
        help_text="Date de début de l'indisponibilité"
    )
    date_fin = models.DateField(
        help_text="Date de fin de l'indisponibilité"
    )
    toute_la_journee = models.BooleanField(
        default=True,
        help_text="Si vrai, toute la plage de dates est bloquée"
    )
    heure_debut = models.TimeField(
        null=True,
        blank=True,
        help_text="Heure de début si indisponibilité partielle"
    )
    heure_fin = models.TimeField(
        null=True,
        blank=True,
        help_text="Heure de fin si indisponibilité partielle"
    )
    motif = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Motif de l'absence (ex: Congé annuel, Formation, Garde)"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Indique si cette indisponibilité est actuellement active"
    )

    class Meta:
        verbose_name = "Indisponibilité Médecin"
        verbose_name_plural = "Indisponibilités Médecins"
        ordering = ["-date_debut", "-id"]

    def __str__(self):
        return f"{self.medecin} - Indisponible du {self.date_debut} au {self.date_fin} ({self.motif or 'Absence'})"

