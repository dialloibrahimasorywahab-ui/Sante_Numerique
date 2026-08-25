from django.contrib import admin
from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'medecin', 'date_cons', 'frais', 'actif')
    list_filter = ('actif', 'date_cons')
    search_fields = ('patient__idUtilisateur__nom', 'medecin__idUtilisateur__nom', 'diagnostic')
