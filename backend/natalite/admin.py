# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Natalite


@admin.register(Natalite)
class NataliteAdmin(admin.ModelAdmin):
    list_display = (
        'id_nouveau_ne',
        'prenom_nouveau_ne',
        'nom_nouveau_ne',
        'date_naissance',
        'sexe',
        'id_patient',
        'id_medecin',
        'poids',
        'taille',
    )
    list_filter = ('sexe', 'date_naissance', 'groupe_sanguin')
    search_fields = (
        'prenom_nouveau_ne',
        'nom_nouveau_ne',
        'lieu_naissance',
        'observation',
        'id_patient__id_utilisateur__nom',
        'id_patient__id_utilisateur__prenom',
    )
    ordering = ('-date_naissance', '-id_nouveau_ne')
