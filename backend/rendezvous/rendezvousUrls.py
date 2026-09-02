# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_rendezvous, name="create_rendezvous"),
    path("creneaux/", views.get_creneaux_disponibles, name="get_creneaux_disponibles"),
    path("mes-rendezvous/", views.get_mes_rendezvous, name="get_mes_rendezvous"),
    path("all/", views.get_all_rendezvous, name="get_all_rendezvous"),
    path("statut/<str:statut>/", views.get_rendezvous_by_statut, name="get_rendezvous_by_statut"),
    path("patient/<int:patient_id>/", views.get_rendezvous_by_patient, name="get_rendezvous_by_patient"),
    path("medecin/<int:medecin_id>/", views.get_rendezvous_by_medecin, name="get_rendezvous_by_medecin"),
    path("medecin/<int:medecin_id>/creneaux/", views.get_creneaux_disponibles, name="get_medecin_creneaux"),
    path("<int:rdv_id>/", views.get_rendezvous, name="get_rendezvous"),
    path("<int:rdv_id>/update/", views.update_rendezvous, name="update_rendezvous"),
    path("<int:rdv_id>/confirmer/", views.confirmer_rendezvous, name="confirmer_rendezvous"),
    path("<int:rdv_id>/annuler/", views.annuler_rendezvous, name="annuler_rendezvous"),
    path("<int:rdv_id>/terminer/", views.terminer_rendezvous, name="terminer_rendezvous"),
    path("<int:rdv_id>/delete/", views.delete_rendezvous, name="delete_rendezvous"),
]

