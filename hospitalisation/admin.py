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
        'patient__idUtilisateur__nom',
        'patient__idUtilisateur__prenom',
        'medecin__idUtilisateur__nom',
        'motif',
    )
    ordering = ('-date_entree',)
