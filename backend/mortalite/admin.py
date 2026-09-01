# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Mortalite


@admin.register(Mortalite)
class MortaliteAdmin(admin.ModelAdmin):
    list_display = (
        'id_deces',
        'id_patient',
        'date_deces',
        'heure_deces',
        'cause_deces',
        'id_medecin',
    )
    list_filter = ('date_deces',)
    search_fields = (
        'cause_deces',
        'lieu_deces',
        'observation',
        'id_patient__id_utilisateur__nom',
        'id_patient__id_utilisateur__prenom',
    )
    ordering = ('-date_deces', '-id_deces')
