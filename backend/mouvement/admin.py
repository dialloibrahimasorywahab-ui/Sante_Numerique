from django.contrib import admin
from .models import MouvementPatient


@admin.register(MouvementPatient)
class MouvementPatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sejour",
        "type_mouvement",
        "localisation_origine",
        "localisation_destination",
        "date_mouvement",
        "motif",
    )
    list_filter = ("type_mouvement", "date_mouvement")
    search_fields = ("sejour__reference", "motif")
