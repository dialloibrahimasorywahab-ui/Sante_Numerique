from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class LocalisationPatient(models.Model):
    """
    Représente la localisation physique d'un patient à un instant T durant son séjour.
    Distingue la localisation actuelle (est_actuelle=True) de l'historique de présence.
    """
    id = models.AutoField(primary_key=True)

    sejour = models.ForeignKey(
        "sejour.Sejour",
        on_delete=models.CASCADE,
        related_name="localisations",
        help_text="Séjour associé"
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="localisations_patients",
        help_text="Pôle / Service de soins"
    )

    batiment = models.ForeignKey(
        "batiment.Batiment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localisations_patients",
        help_text="Bâtiment physique (facultatif si zone d'accueil/urgence)"
    )

    chambre = models.ForeignKey(
        "chambre.Chambre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localisations_patients",
        help_text="Chambre d'hospitalisation"
    )

    lit = models.ForeignKey(
        "lit.Lit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localisations_patients",
        help_text="Lit attribué (facultatif si attente, box ou brancard)"
    )

    date_debut = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure de début d'occupation de cet emplacement"
    )

    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure de fin (nulle tant que le patient y séjourne)"
    )

    est_actuelle = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indique si cette localisation est celle où se trouve actuellement le patient"
    )

    motif = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Motif de l'affectation ou du séjour à cet endroit"
    )

    commentaire = models.TextField(
        blank=True,
        null=True,
        help_text="Notes ou instructions complémentaires"
    )

    enregistre_par = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localisations_enregistrees"
    )

    class Meta:
        verbose_name = "Localisation du Patient"
        verbose_name_plural = "Localisations des Patients"
        ordering = ["-date_debut", "-id"]

    def __str__(self):
        lieu_elements = [str(self.service.get_nom_service_display() if hasattr(self.service, "get_nom_service_display") else self.service)]
        if self.batiment:
            lieu_elements.append(self.batiment.nom)
        if self.chambre:
            lieu_elements.append(f"Ch. {self.chambre.numero_chambre}")
        if self.lit:
            lieu_elements.append(f"Lit {self.lit.numero_lit or self.lit.id}")
        lieu = " / ".join(lieu_elements)
        statut = "ACTUELLE" if self.est_actuelle else "PASSÉE"
        ref_sejour = self.sejour.reference if self.sejour_id else "Séjour inconnu"
        return f"{ref_sejour} @ {lieu} ({statut})"

    def clean(self):
        super().clean()
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError({
                "date_fin": "La date de fin ne peut pas précéder la date de début de localisation."
            })

        # Cohérence de la hiérarchie spatiale
        if self.lit:
            if not self.chambre:
                self.chambre = self.lit.chambre
            elif self.lit.chambre_id != self.chambre.id:
                raise ValidationError({
                    "lit": f"Le lit #{self.lit.id} n'appartient pas à la chambre #{self.chambre.id} sélectionnée."
                })

        if self.chambre:
            if not self.batiment:
                self.batiment = self.chambre.batiment
            elif self.chambre.batiment_id != self.batiment.id_batiment:
                raise ValidationError({
                    "chambre": f"La chambre #{self.chambre.id} n'appartient pas au bâtiment #{self.batiment.id_batiment}."
                })
