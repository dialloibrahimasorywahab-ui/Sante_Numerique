# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Ordonnance


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'consultation', 'date_ordonnance', 'actif')
    list_filter = ('actif', 'date_ordonnance')
    search_fields = ('reference', 'observation')
