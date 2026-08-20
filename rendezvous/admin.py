# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'medecin', 'date_rdv', 'heure', 'statut')
    list_filter = ('statut', 'date_rdv', 'medecin')
    search_fields = (
        'motif',
        'patient__idUtilisateur__nom',
        'patient__idUtilisateur__prenom',
        'medecin__idUtilisateur__nom',
        'medecin__idUtilisateur__prenom'
    )
