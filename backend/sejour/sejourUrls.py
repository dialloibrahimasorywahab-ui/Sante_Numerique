from django.urls import path
from .views import (
    sejour_list_create_view,
    sejour_detail_view,
    sejour_autoriser_sortie_view,
    sejour_cloturer_view,
    sejour_synthese_view,
    sejour_dashboard_stats_view,
)

urlpatterns = [
    path("", sejour_list_create_view, name="sejour-list-create"),
    path("statistiques-dashboard/", sejour_dashboard_stats_view, name="sejour-dashboard-stats"),
    path("<int:pk>/", sejour_detail_view, name="sejour-detail"),
    path("<int:pk>/autoriser-sortie/", sejour_autoriser_sortie_view, name="sejour-autoriser-sortie"),
    path("<int:pk>/cloturer/", sejour_cloturer_view, name="sejour-cloturer"),
    path("<int:pk>/dossier-synthese/", sejour_synthese_view, name="sejour-synthese"),
]
