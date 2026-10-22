from django.contrib import admin
from .models import LocalisationPatient


@admin.register(LocalisationPatient)
class LocalisationPatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sejour",
        "service",
        "batiment",
        "chambre",
        "lit",
        "date_debut",
        "date_fin",
        "est_actuelle",
    )
    list_filter = ("est_actuelle", "service", "batiment")
    search_fields = ("sejour__reference", "chambre__numero_chambre", "lit__numero_lit")
