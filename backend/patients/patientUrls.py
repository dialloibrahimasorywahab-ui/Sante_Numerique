from django.urls import path
from . import views


urlpatterns = [

    # Créer un patient
    path(
        "",
        views.create_patient,
        name="create_patient"
    ),

    # Récupérer tous les patients
    path(
        "all/",
        views.get_all_patient,
        name="get_all_patient"
    ),

    # Récupérer un patient par son ID
    path(
        "<int:patient_id>/",
        views.get_patient,
        name="get_patient"
    ),

    # Modifier un patient
    path(
        "<int:patient_id>/update/",
        views.update_patient,
        name="update_patient"
    ),

    # Supprimer un patient
    path(
        "<int:patient_id>/delete/",
        views.delete_patient,
        name="delete_patient"
    ),
]
