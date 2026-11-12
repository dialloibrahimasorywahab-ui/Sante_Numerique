from django.urls import path
from .views import list_create_documents, get_document_detail, download_document_file

urlpatterns = [
    path('', list_create_documents, name='document-list-create'),
    path('<int:document_id>/', get_document_detail, name='document-detail'),
    path('<int:document_id>/download/', download_document_file, name='document-download'),
]
