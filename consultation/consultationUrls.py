from django.urls import path
from . import views

urlpatterns = [
    path('', views.consultation_list_create_view, name='consultation-list-create'),
    path('<int:pk>/', views.consultation_detail_view, name='consultation-detail'),
    path('<int:pk>/delete/', views.consultation_delete_view, name='consultation-delete'),
]
