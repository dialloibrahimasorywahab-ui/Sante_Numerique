from django.contrib import admin
from .models import Chambre


@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_chambre', 'batiment', 'type_chambre', 'capacite', 'statut')
    list_filter = ('statut', 'type_chambre', 'batiment')
    search_fields = ('numero_chambre', 'batiment__nom')


