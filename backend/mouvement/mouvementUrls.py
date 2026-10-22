from django.urls import path
from .views import mouvement_list_view, mouvement_transfert_view, mouvement_detail_view

urlpatterns = [
    path("", mouvement_list_view, name="mouvement-list"),
    path("transfert/", mouvement_transfert_view, name="mouvement-transfert"),
    path("<int:pk>/", mouvement_detail_view, name="mouvement-detail"),
]
