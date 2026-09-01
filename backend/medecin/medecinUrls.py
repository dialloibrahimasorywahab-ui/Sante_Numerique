from django.urls import path
from . import views


urlpatterns = [

    # Créer un médecin
    path(
        "",
        views.create_medecin,
        name="create_medecin"
    ),

    # Récupérer tous les médecins
    path(
        "all/",
        views.get_all_medecin,
        name="get_all_medecin"
    ),

    # Récupérer les médecins par service / spécialité
    path(
        "service/<str:specialite>/",
        views.get_medecins_by_specialite,
        name="get_medecins_by_service"
    ),
    path(
        "specialite/<str:specialite>/",
        views.get_medecins_by_specialite,
        name="get_medecins_by_specialite"
    ),

    # Récupérer un médecin par son ID
    path(
        "<int:medecin_id>/",
        views.get_medecin,
        name="get_medecin"
    ),

    # Modifier un médecin
    path(
        "<int:medecin_id>/update/",
        views.update_medecin,
        name="update_medecin"
    ),

    # Supprimer un médecin
    path(
        "<int:medecin_id>/delete/",
        views.delete_medecin,
        name="delete_medecin"
    ),
]
