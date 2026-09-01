from django.urls import path
from . import views


urlpatterns = [

    # Créer un membre du personnel
    path(
        "",
        views.create_personnel,
        name="create_personnel"
    ),

    # Récupérer tout le personnel
    path(
        "all/",
        views.get_all_personnel,
        name="get_all_personnel"
    ),

    # Récupérer le personnel par type / catégorie (ex: INFIRMIER, ADMINISTRATIF)
    path(
        "type/<str:type_personnel>/",
        views.get_personnel_by_type,
        name="get_personnel_by_type"
    ),

    # Récupérer un membre du personnel par son ID
    path(
        "<int:personnel_id>/",
        views.get_personnel,
        name="get_personnel"
    ),

    # Modifier un membre du personnel
    path(
        "<int:personnel_id>/update/",
        views.update_personnel,
        name="update_personnel"
    ),

    # Supprimer un membre du personnel
    path(
        "<int:personnel_id>/delete/",
        views.delete_personnel,
        name="delete_personnel"
    ),
]
