from django.contrib import admin
from .models import FraisConsultation


@admin.register(FraisConsultation)
class FraisConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'montant', 'statut', 'date_paiement', 'actif')
    list_filter = ('statut', 'actif')
    search_fields = ('description',)
