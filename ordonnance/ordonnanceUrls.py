# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ordonnance_list_create_view, name='ordonnance-list-create'),
    path('<int:pk>/', views.ordonnance_detail_view, name='ordonnance-detail'),
    path('<int:pk>/delete/', views.ordonnance_delete_view, name='ordonnance-delete'),
]
