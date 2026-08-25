from django.urls import path
from . import views

urlpatterns = [
    path('', views.frais_list_create_view, name='frais-list-create'),
    path('<int:pk>/', views.frais_detail_view, name='frais-detail'),
    path('<int:pk>/payer/', views.frais_payer_view, name='frais-payer'),
    path('<int:pk>/delete/', views.frais_delete_view, name='frais-delete'),
]
