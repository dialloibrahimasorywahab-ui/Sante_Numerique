# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_batiment, name="create_batiment"),
    path("all/", views.get_all_batiments, name="get_all_batiments"),
    path("<int:batiment_id>/", views.get_batiment, name="get_batiment"),
    path("<int:batiment_id>/chambres/", views.get_batiment_chambres, name="get_batiment_chambres"),
    path("<int:batiment_id>/update/", views.update_batiment, name="update_batiment"),
    path("<int:batiment_id>/delete/", views.delete_batiment, name="delete_batiment"),
]

