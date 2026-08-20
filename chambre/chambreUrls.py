# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_chambre, name="create_chambre"),
    path("all/", views.get_all_chambres, name="get_all_chambres"),
    path("type/<str:type_chambre>/", views.get_chambres_by_type, name="get_chambres_by_type"),
    path("statut/<str:statut>/", views.get_chambres_by_statut, name="get_chambres_by_statut"),
    path("<int:chambre_id>/", views.get_chambre, name="get_chambre"),
    path("<int:chambre_id>/update/", views.update_chambre, name="update_chambre"),
    path("<int:chambre_id>/delete/", views.delete_chambre, name="delete_chambre"),
]


