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

    # Disponibilités et créneaux réguliers du médecin
    path(
        "disponibilites/",
        views.disponibilites_list_create_view,
        name="medecin_disponibilites_list_create"
    ),
    path(
        "disponibilites/bulk/",
        views.disponibilites_bulk_view,
        name="medecin_disponibilites_bulk"
    ),
    path(
        "disponibilites/<int:pk>/",
        views.disponibilite_detail_view,
        name="medecin_disponibilite_detail"
    ),

    # Indisponibilités, congés et absences exceptionnelles
    path(
        "indisponibilites/",
        views.indisponibilites_list_create_view,
        name="medecin_indisponibilites_list_create"
    ),
    path(
        "indisponibilites/<int:pk>/",
        views.indisponibilite_detail_view,
        name="medecin_indisponibilite_detail"
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
