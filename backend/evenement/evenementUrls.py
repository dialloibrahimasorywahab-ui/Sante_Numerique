from django.urls import path
from .views import evenement_list_create_view, evenement_detail_view

urlpatterns = [
    path("", evenement_list_create_view, name="evenement-list-create"),
    path("<int:pk>/", evenement_detail_view, name="evenement-detail"),
]
