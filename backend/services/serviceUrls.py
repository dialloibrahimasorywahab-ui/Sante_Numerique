from django.urls import path
from . import views


urlpatterns = [

    # Créer un service
    path(
        "",
        views.create_service,
        name="create_service"
    ),

    # Récupérer tous les services
    path(
        "all/",
        views.get_all_services,
        name="get_all_services"
    ),

    # Récupérer un service par son ID
    path(
        "<int:service_id>/",
        views.get_service,
        name="get_service"
    ),

    # Modifier un service
    path(
        "<int:service_id>/update/",
        views.update_service,
        name="update_service"
    ),

    # Supprimer un service
    path(
        "<int:service_id>/delete/",
        views.delete_service,
        name="delete_service"
    ),
]
