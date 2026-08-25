# pyrefly: ignore [missing-import]
from django.urls import path
# pyrefly: ignore [missing-import]
from . import views

urlpatterns = [
    path('', views.get_all_natality, name='get_all_natality'),
    path('create/', views.create_naissance, name='create_naissance'),
    path('<int:id_natality>/', views.get_natality, name='get_natality'),
    path('<int:natality_id>/update/', views.update_natality, name='update_natality'),
    path('<int:natality_id>/delete/', views.delete_natality, name='delete_natality'),
    path('sexe/<str:sexe>/', views.get_natalities_by_sexe, name='get_natalities_by_sexe'),
    path('patient/<int:patient_id>/', views.get_natalities_by_patient, name='get_natalities_by_patient'),
    path('medecin/<int:medecin_id>/', views.get_natalities_by_medecin, name='get_natalities_by_medecin'),
]
