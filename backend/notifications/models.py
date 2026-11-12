from django.db import models
from users.models import User


class NotificationHospitaliere(models.Model):
    """
    Système d'alertes et de notifications en temps réel pour l'établissement hospitalier.
    Notifie instantanément les praticiens et cadres soignants pour :
    - L'affectation immédiate de lits d'urgences / réanimation
    - L'arrivée d'un patient en salle d'attente
    - Les alertes cliniques et programmations prioritaires
    """

    class TypeNotification(models.TextChoices):
        LIT_URGENCE = "LIT_URGENCE", "Lit d'Urgence / Réanimation"
        PATIENT_ARRIVE = "PATIENT_ARRIVE", "Patient arrivé en salle d'attente"
        NOUVEAU_RDV = "NOUVEAU_RDV", "Nouveau rendez-vous"
        HOSPITALISATION = "HOSPITALISATION", "Admission / Sortie hospitalière"
        ALERTE_CLINIQUE = "ALERTE_CLINIQUE", "Alerte Clinique Urgente"
        RAPPEL_RDV = "RAPPEL_RDV", "Rappel de rendez-vous"
        PRISE_MEDICAMENT = "PRISE_MEDICAMENT", "Prise de médicament / traitement"
        INFO = "INFO", "Information Générale"

    class DestinataireRole(models.TextChoices):
        TOUS = "TOUS", "Tout le personnel soignant et administratif"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateurs"
        MEDECIN = "MEDECIN", "Médecins"
        INFIRMIER = "INFIRMIER", "Infirmiers / Soignants"
        PATIENT = "PATIENT", "Patient spécifique"

    id_notification = models.AutoField(primary_key=True)

    type_notification = models.CharField(
        max_length=50,
        choices=TypeNotification.choices,
        default=TypeNotification.INFO,
        help_text="Typologie de l'événement"
    )

    titre = models.CharField(
        max_length=200,
        help_text="Intitulé concis de l'alerte"
    )

    message = models.TextField(
        help_text="Détail complet de la notification"
    )

    donnees = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées d'événement (id_lit, id_patient, id_rdv, etc.)"
    )

    destinataire_role = models.CharField(
        max_length=30,
        choices=DestinataireRole.choices,
        default=DestinataireRole.TOUS,
        help_text="Groupe ou rôle visé par la notification"
    )

    destinataire_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications_recues",
        db_column="id_utilisateur",
        help_text="Utilisateur spécifique ciblé (optionnel)"
    )

    lu = models.BooleanField(
        default=False,
        help_text="Indique si la notification a été acquittée"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
        help_text="Horodatage d'émission"
    )

    actif = models.BooleanField(
        default=True,
        help_text="Archivage logique"
    )

    class Meta:
        verbose_name = "Notification Hospitalière"
        verbose_name_plural = "Notifications Hospitalières"
        ordering = ["-date_creation", "-id_notification"]

    def __str__(self):
        return f"[{self.get_type_notification_display()}] {self.titre} ({self.date_creation.strftime('%H:%M')})"

    @property
    def id(self) -> int:
        return self.id_notification

    # Propriétés de compatibilité camelCase
    @property
    def idNotification(self) -> int:
        return self.id_notification

    @property
    def typeNotification(self) -> str:
        return self.type_notification

    @property
    def destinataireRole(self) -> str:
        return self.destinataire_role

    @property
    def dateCreation(self):
        return self.date_creation
