# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'medecin', 'date_rdv', 'heure', 'statut')
    list_filter = ('statut', 'date_rdv', 'medecin')
    search_fields = (
        'motif',
        'patient__id_utilisateur__nom',
        'patient__id_utilisateur__prenom',
        'medecin__id_utilisateur__nom',
        'medecin__id_utilisateur__prenom'
    )
