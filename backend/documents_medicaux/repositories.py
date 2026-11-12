from typing import Optional, List
from django.db.models import QuerySet, Q
from common.repositories import BaseRepository
from .models import DocumentMedical


class DocumentMedicalRepository(BaseRepository[DocumentMedical]):
    """
    Repository d'accès aux données pour les documents médicaux (GED).
    Hérite des opérations standardisées de BaseRepository (CRUD, soft/hard delete).
    """

    def __init__(self):
        super().__init__(model=DocumentMedical)

    def get_by_patient(
        self,
        patient_id: int,
        categorie: Optional[str] = None,
        actif_only: bool = True
    ) -> QuerySet[DocumentMedical]:
        qs = self.get_all(actif_only=actif_only, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur', 'consultation'])
        qs = qs.filter(patient_id=patient_id)
        if categorie:
            qs = qs.filter(categorie__iexact=categorie)
        return qs

    def get_by_medecin(
        self,
        medecin_id: int,
        actif_only: bool = True
    ) -> QuerySet[DocumentMedical]:
        qs = self.get_all(actif_only=actif_only, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur', 'consultation'])
        return qs.filter(medecin_id=medecin_id)

    def search_documents(
        self,
        query: str,
        patient_id: Optional[int] = None,
        categorie: Optional[str] = None,
        actif_only: bool = True
    ) -> QuerySet[DocumentMedical]:
        qs = self.get_all(actif_only=actif_only, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur'])
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if categorie:
            qs = qs.filter(categorie__iexact=categorie)

        clean_q = str(query).strip() if query else ""
        if clean_q:
            qs = qs.filter(
                Q(titre__icontains=clean_q) |
                Q(observation__icontains=clean_q) |
                Q(nom_original__icontains=clean_q) |
                Q(patient__id_utilisateur__nom__icontains=clean_q) |
                Q(patient__id_utilisateur__prenom__icontains=clean_q)
            )
        return qs
