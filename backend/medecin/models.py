from django.db import models
from users.models import User
from simple_history.models import HistoricalRecords


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

    history = HistoricalRecords()

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

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="disponibilites",
        db_column="id_medecin"
    )
    jour_semaine = models.IntegerField(
        choices=JourSemaine.choices,
        help_text="0=Lundi, 1=Mardi, ..., 6=Dimanche"
    )
    heure_debut = models.TimeField(
        default="08:00:00",
        help_text="Heure de début de consultation"
    )
    heure_fin = models.TimeField(
        default="16:00:00",
        help_text="Heure de fin de consultation"
    )
    pause_debut = models.TimeField(
        null=True,
        blank=True,
        default="12:00:00",
        help_text="Début de pause déjeuner (optionnel)"
    )
    pause_fin = models.TimeField(
        null=True,
        blank=True,
        default="13:00:00",
        help_text="Fin de pause déjeuner (optionnel)"
    )
    duree_consultation = models.IntegerField(
        default=30,
        help_text="Durée moyenne d'un créneau en minutes (ex: 20, 30, 45)"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Indique si le médecin consulte ce jour-là"
    )


    @property
    def duree_creneau(self):
        return self.duree_consultation

    @duree_creneau.setter
    def duree_creneau(self, value):
        self.duree_consultation = value

    class Meta:
        unique_together = ("medecin", "jour_semaine")
        ordering = ["jour_semaine", "heure_debut"]
        verbose_name = "Disponibilité Médecin"
        verbose_name_plural = "Disponibilités Médecins"

    def __str__(self):
        jour_label = self.get_jour_semaine_display()
        statut = f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}" if self.actif else "Non disponible"
        return f"{self.medecin} | {jour_label} : {statut}"


class IndisponibiliteMedecin(models.Model):
    """
    Périodes d'absence ponctuelle d'un médecin (congés, arrêts, réunions, etc.).
    Bloque la prise de rendez-vous sur cette plage temporelle.
    """
    class TypeIndisponibilite(models.TextChoices):
        CONGE = "CONGE", "Congés"
        MALADIE = "MALADIE", "Arrêt Maladie"
        FORMATION = "FORMATION", "Formation / Séminaire"
        GARDE = "GARDE", "Garde Exceptionnelle"
        AUTRE = "AUTRE", "Autre absence"

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="indisponibilites",
        db_column="id_medecin"
    )
    titre = models.CharField(
        max_length=150,
        default="Absence",
        help_text="Intitulé ou motif court de l'absence"
    )
    type_indisponibilite = models.CharField(
        max_length=30,
        choices=TypeIndisponibilite.choices,
        default=TypeIndisponibilite.CONGE
    )
    date_debut = models.DateTimeField(
        help_text="Date et heure de début de l'absence"
    )
    date_fin = models.DateTimeField(
        help_text="Date et heure de fin de l'absence"
    )
    commentaire = models.TextField(
        blank=True,
        null=True,
        help_text="Précisions utiles pour l'équipe ou le secrétariat"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Permet d'annuler ou désactiver une absence sans la supprimer"
    )

    @property
    def motif(self):
        return self.titre

    @motif.setter
    def motif(self, value):
        self.titre = value


    class Meta:
        ordering = ["-date_debut"]
        verbose_name = "Indisponibilité Médecin"
        verbose_name_plural = "Indisponibilités Médecins"

    def __str__(self):
        debut_str = self.date_debut.strftime("%d/%m/%Y %H:%M")
        fin_str = self.date_fin.strftime("%d/%m/%Y %H:%M")
        return f"{self.medecin} | {self.get_type_indisponibilite_display()} du {debut_str} au {fin_str}"
