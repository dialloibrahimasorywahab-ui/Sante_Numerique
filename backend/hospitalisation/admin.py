# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Hospitalisation


@admin.register(Hospitalisation)
class HospitalisationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'medecin',
        'lit',
        'date_entree',
        'date_sortie',
        'statut',
        'actif',
    )
    list_filter = ('statut', 'actif', 'date_entree')
    search_fields = (
        'patient__id_utilisateur__nom',
        'patient__id_utilisateur__prenom',
        'medecin__id_utilisateur__nom',
        'motif',
    )
    ordering = ('-date_entree',)
