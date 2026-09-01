from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_lit, name="create_lit"),
    path("all/", views.get_all_lits, name="get_all_lits"),
    path("etat/<str:etat>/", views.get_lits_by_etat, name="get_lits_by_etat"),
    path("<int:lit_id>/", views.get_lit, name="get_lit"),
    path("<int:lit_id>/update/", views.update_lit, name="update_lit"),
    path("<int:lit_id>/delete/", views.delete_lit, name="delete_lit"),
]

