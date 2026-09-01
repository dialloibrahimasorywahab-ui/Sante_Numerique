from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_mortalite, name='get_all_mortalite'),
    path('create/', views.create_deces, name='create_deces'),
    path('<int:id_deces>/', views.get_mortalite, name='get_mortalite'),
    path('<int:deces_id>/update/', views.update_mortalite, name='update_mortalite'),
    path('<int:deces_id>/delete/', views.delete_mortalite, name='delete_mortalite'),
]
