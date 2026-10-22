from django.contrib import admin
from .models import EvenementParcours


@admin.register(EvenementParcours)
class EvenementParcoursAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sejour",
        "type_evenement",
        "titre",
        "importance",
        "date_evenement",
        "declare_par",
    )
    list_filter = ("type_evenement", "importance", "date_evenement")
    search_fields = ("titre", "description", "sejour__reference")
