# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Batiment


@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = ('id_batiment', 'nom', 'nombre_chambre', 'actif')
    search_fields = ('nom', 'description')
    list_filter = ('actif',)

