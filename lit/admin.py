# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Lit


@admin.register(Lit)
class LitAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_lit', 'chambre', 'etat')
    list_filter = ('etat', 'chambre__batiment')
    search_fields = ('numero_lit', 'chambre__numero_chambre', 'chambre__batiment__nom')
