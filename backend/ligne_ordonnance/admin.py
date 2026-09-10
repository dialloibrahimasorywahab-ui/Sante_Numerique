from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import LigneOrdonnance


@admin.register(LigneOrdonnance)
class LigneOrdonnanceAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'medicament', 'dosage', 'forme', 'posologie', 'duree_traitement', 'quantite', 'ordonnance', 'actif')
    list_filter = ('forme', 'actif')
    search_fields = ('medicament', 'posologie', 'instructions')
