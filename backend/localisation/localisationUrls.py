from django.urls import path
from .views import localisation_list_create_view, localisation_detail_view

urlpatterns = [
    path("", localisation_list_create_view, name="localisation-list-create"),
    path("<int:pk>/", localisation_detail_view, name="localisation-detail"),
]
