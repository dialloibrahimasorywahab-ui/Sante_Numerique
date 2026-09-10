from django.urls import path
from .views import ligne_ordonnance_list_create_view, ligne_ordonnance_detail_view

urlpatterns = [
    path('', ligne_ordonnance_list_create_view, name='ligne_ordonnance_list_create'),
    path('<int:pk>/', ligne_ordonnance_detail_view, name='ligne_ordonnance_detail'),
]
