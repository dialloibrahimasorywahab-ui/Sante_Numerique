from django.db import models
from django.utils import timezone


class MouvementPatient(models.Model):
    """
    Enregistre chaque déplacement physique significatif du patient (transfert, admission, sortie).
    Historique chronologique médico-légal immuable.
    """

    class TypeMouvement(models.TextChoices):
        ADMISSION = "ADMISSION", "Admission initiale"
        TRANSFERT_SERVICE = "TRANSFERT_SERVICE", "Transfert de service"
        CHANGEMENT_CHAMBRE = "CHANGEMENT_CHAMBRE", "Changement de chambre"
        CHANGEMENT_LIT = "CHANGEMENT_LIT", "Changement de lit"
        DEPART_EXAMEN = "DEPART_EXAMEN", "Départ pour examen / bloc"
        RETOUR_EXAMEN = "RETOUR_EXAMEN", "Retour d'examen / bloc"
        SORTIE_TEMPORAIRE = "SORTIE_TEMPORAIRE", "Sortie temporaire / permission"
        RETOUR_SORTIE_TEMPO = "RETOUR_SORTIE_TEMPO", "Retour de permission"
        SORTIE_DEFINITIVE = "SORTIE_DEFINITIVE", "Sortie définitive"

    id = models.AutoField(primary_key=True)

    sejour = models.ForeignKey(
        "sejour.Sejour",
        on_delete=models.CASCADE,
        related_name="mouvements",
        help_text="Séjour associé"
    )

    localisation_origine = models.ForeignKey(
        "localisation.LocalisationPatient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements_depart",
        help_text="Emplacement de provenance"
    )

    localisation_destination = models.ForeignKey(
        "localisation.LocalisationPatient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements_arrivee",
        help_text="Nouvel emplacement"
    )

    date_mouvement = models.DateTimeField(
        default=timezone.now,
        help_text="Horodatage précis du déplacement"
    )

    type_mouvement = models.CharField(
        max_length=40,
        choices=TypeMouvement.choices,
        default=TypeMouvement.TRANSFERT_SERVICE
    )

    motif = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Motif clinique ou logistique du déplacement"
    )

    commentaire = models.TextField(
        blank=True,
        null=True
    )

    enregistre_par = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements_enregistres",
        help_text="Utilisateur ayant validé le transfert"
    )

    class Meta:
        verbose_name = "Mouvement du Patient"
        verbose_name_plural = "Mouvements des Patients"
        ordering = ["-date_mouvement", "-id"]

    def __str__(self):
        ref = self.sejour.reference if self.sejour_id else "Séjour inconnu"
        return f"{ref} - {self.get_type_mouvement_display()} ({self.date_mouvement.strftime('%d/%m/%Y %H:%M')})"
