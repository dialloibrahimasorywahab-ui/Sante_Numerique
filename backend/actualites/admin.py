from django.contrib import admin
from .models import CategorieActualite, Actualite


@admin.register(CategorieActualite)
class CategorieActualiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'slug', 'couleur', 'actif', 'date_creation')
    list_filter = ('actif',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'categorie', 'statut', 'est_a_la_une', 'date_publication', 'vues')
    list_filter = ('statut', 'est_a_la_une', 'categorie', 'date_publication')
    search_fields = ('titre', 'resume', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_publication'
    raw_id_fields = ('auteur',)

