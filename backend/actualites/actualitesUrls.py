from django.urls import path
from .views import (
    categories_list_create_view,
    categorie_detail_view,
    actualites_list_create_view,
    actualite_detail_view,
    actualite_suggestions_view,
)

urlpatterns = [
    # Catégories
    path('categories/', categories_list_create_view, name='actualites_categories_list_create'),
    path('categories/<int:pk>/', categorie_detail_view, name='actualites_categorie_detail'),

    # Suggestions d'articles
    path('<str:slug_or_id>/suggestions/', actualite_suggestions_view, name='actualite_suggestions'),

    # Articles
    path('', actualites_list_create_view, name='actualites_list_create'),
    path('<str:slug_or_id>/', actualite_detail_view, name='actualite_detail'),
]

