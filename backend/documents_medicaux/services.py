import os
from typing import Optional, Tuple
from django.core.files.base import ContentFile
from django.db import transaction
from common.services import BaseService
from .models import DocumentMedical
from .repositories import DocumentMedicalRepository
from .encryption import encrypt_bytes, decrypt_bytes, calculate_sha256


class DocumentMedicalService(BaseService[DocumentMedical]):
    """
    Service métier pour la gestion du cycle de vie des documents médicaux :
    - Chiffrement au repos transparent (AES-256 Fernet)
    - Empreinte cryptographique SHA-256 pour audit et intégrité
    - Déchiffrement sécurisé à la volée pour consultation
    """

    repository: DocumentMedicalRepository

    def __init__(self, repository: Optional[DocumentMedicalRepository] = None):
        super().__init__(repository=repository or DocumentMedicalRepository())

    @transaction.atomic
    def upload_document(
        self,
        patient,
        titre: str,
        uploaded_file,
        categorie: str = DocumentMedical.Categorie.AUTRE,
        medecin=None,
        consultation=None,
        date_document=None,
        observation: str = ""
    ) -> DocumentMedical:
        """
        Traite un fichier médical brut, génère son empreinte SHA-256,
        le chiffre avec Fernet AES-256 et le persiste en base.
        """
        raw_bytes = uploaded_file.read()
        original_size = len(raw_bytes)
        original_name = uploaded_file.name
        content_type = getattr(uploaded_file, 'content_type', 'application/octet-stream')

        # 1. Calcul de l'empreinte de contrôle
        checksum = calculate_sha256(raw_bytes)

        # 2. Chiffrement fort au repos
        encrypted_bytes = encrypt_bytes(raw_bytes)

        # 3. Création du fichier chiffré stocké (nom sécurisé)
        safe_filename = f"enc_{checksum[:16]}_{os.path.basename(original_name)}"
        encrypted_content_file = ContentFile(encrypted_bytes, name=safe_filename)

        # 4. Enregistrement en base de données
        create_kwargs = {
            "patient": patient,
            "medecin": medecin,
            "consultation": consultation,
            "titre": titre.strip(),
            "categorie": categorie,
            "fichier": encrypted_content_file,
            "nom_original": original_name,
            "taille_octets": original_size,
            "type_mime": content_type,
            "checksum_sha256": checksum,
            "chiffre": True,
            "observation": observation,
        }
        if date_document:
            if hasattr(date_document, 'date'):
                date_document = date_document.date()
            create_kwargs["date_document"] = date_document
        else:
            from django.utils import timezone
            create_kwargs["date_document"] = timezone.localdate()

        return self.create(**create_kwargs)

    def get_decrypted_content(self, document: DocumentMedical) -> Tuple[bytes, str, str]:
        """
        Lit le fichier stocké, le déchiffre si nécessaire et retourne :
        (contenu_binaire_original, nom_de_fichier_original, type_mime)
        """
        document.fichier.open('rb')
        try:
            stored_bytes = document.fichier.read()
        finally:
            document.fichier.close()

        if document.chiffre:
            decrypted_bytes = decrypt_bytes(stored_bytes)
        else:
            decrypted_bytes = stored_bytes

        return decrypted_bytes, document.nom_original or "document_medical.bin", document.type_mime
