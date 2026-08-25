# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hospitalisation_list_create_view, name='hospitalisation-list-create'),
    path('<int:pk>/', views.hospitalisation_detail_view, name='hospitalisation-detail'),
    path('<int:pk>/cloturer/', views.hospitalisation_cloturer_view, name='hospitalisation-cloturer'),
    path('<int:pk>/delete/', views.hospitalisation_delete_view, name='hospitalisation-delete'),
]
