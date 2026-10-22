from django.contrib import admin
from .models import Sejour, DemandeAnalyse


@admin.register(Sejour)
class SejourAdmin(admin.ModelAdmin):
    list_display = (
        "id_sejour",
        "reference",
        "patient",
        "service_responsable",
        "statut",
        "type_prise_en_charge",
        "date_admission",
        "date_sortie",
        "actif",
    )
    list_filter = ("statut", "type_prise_en_charge", "service_responsable", "actif")
    search_fields = (
        "reference",
        "patient__nom",
        "patient__prenom",
        "patient__numero_securite_sociale",
        "motif_admission",
    )
    readonly_fields = ("reference", "created_at", "updated_at")


@admin.register(DemandeAnalyse)
class DemandeAnalyseAdmin(admin.ModelAdmin):
    list_display = ("id", "type_analyse", "patient", "sejour", "statut", "date_prescription", "actif")
    list_filter = ("statut", "actif")
    search_fields = ("type_analyse", "patient__nom", "sejour__reference")
