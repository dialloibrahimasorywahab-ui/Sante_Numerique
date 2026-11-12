import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from .models import DocumentMedical
from .services import DocumentMedicalService
from .encryption import calculate_sha256, encrypt_bytes, decrypt_bytes


class DocumentMedicalTests(APITestCase):

    def setUp(self):
        # 1. Création utilisateur patient
        self.patient_user = User.objects.create_user(
            login="patient_ged",
            email="patient_ged@hopital.fr",
            password="Password123!",
            nom="Diallo",
            prenom="Fatoumata",
            telephone="0600000088",
            role=User.Role.PATIENT
        )
        self.patient = Patient.objects.create(
            id_utilisateur=self.patient_user,
            sexe="F",
            adresse="Conakry",
            groupe_sanguin="O+",
            date_inscription=timezone.now().date()
        )

        # 2. Création second patient pour test d'isolation
        self.other_patient_user = User.objects.create_user(
            login="other_patient_ged",
            email="other_patient@hopital.fr",
            password="Password123!",
            nom="Camara",
            prenom="Sekou",
            telephone="0600000089",
            role=User.Role.PATIENT
        )
        self.other_patient = Patient.objects.create(
            id_utilisateur=self.other_patient_user,
            sexe="M",
            adresse="Dixinn",
            groupe_sanguin="A+",
            date_inscription=timezone.now().date()
        )

        # 3. Création médecin
        self.doctor_user = User.objects.create_user(
            login="doctor_ged",
            email="doctor_ged@hopital.fr",
            password="Password123!",
            nom="Touré",
            prenom="Dr. Alpha",
            telephone="0600000090",
            role=User.Role.MEDECIN
        )
        self.medecin = Medecin.objects.create(
            id_utilisateur=self.doctor_user,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numero_ordre="ORD-TEST-GED-01",
            date_embauche=timezone.now().date()
        )

        self.service = DocumentMedicalService()

    def test_encryption_and_decryption_cycle(self):
        raw_content = b"DOCUMENT MEDICAL CONFIDENTIEL : RADIOGRAPHIE PULMONAIRE"
        checksum = calculate_sha256(raw_content)

        encrypted = encrypt_bytes(raw_content)
        self.assertNotEqual(encrypted, raw_content)

        decrypted = decrypt_bytes(encrypted)
        self.assertEqual(decrypted, raw_content)
        self.assertEqual(calculate_sha256(decrypted), checksum)

    def test_upload_and_download_flow(self):
        self.client.force_authenticate(user=self.doctor_user)

        pdf_content = b"%PDF-1.4 Fake Medical Scan Data"
        test_file = SimpleUploadedFile("scanner_crane.pdf", pdf_content, content_type="application/pdf")

        # Upload
        response = self.client.post("/documents_medicaux/", {
            "patient": self.patient.id_patient,
            "titre": "Scanner Cérébral sans injection",
            "categorie": DocumentMedical.Categorie.SCANNER,
            "fichier": test_file,
            "observation": "Absence d'anomalie visible."
        }, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc_id = response.data["id_document"]

        doc = DocumentMedical.objects.get(pk=doc_id)
        self.assertTrue(doc.chiffre)
        self.assertEqual(doc.nom_original, "scanner_crane.pdf")
        self.assertEqual(doc.checksum_sha256, calculate_sha256(pdf_content))

        # Téléchargement déchiffré
        download_res = self.client.get(f"/documents_medicaux/{doc_id}/download/")
        self.assertEqual(download_res.status_code, status.HTTP_200_OK)
        self.assertEqual(download_res.content, pdf_content)

    def test_patient_isolation_security(self):
        # Création d'un document pour patient 1 par le médecin
        file = SimpleUploadedFile("analyse.pdf", b"Resultat NFS normal", content_type="application/pdf")
        doc = self.service.upload_document(
            patient=self.patient,
            titre="Bilan NFS",
            uploaded_file=file,
            categorie=DocumentMedical.Categorie.ANALYSE_SANG,
            medecin=self.medecin
        )

        # Patient 1 accède à son document : OK
        self.client.force_authenticate(user=self.patient_user)
        res_p1 = self.client.get(f"/documents_medicaux/{doc.id_document}/download/")
        self.assertEqual(res_p1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_p1.content, b"Resultat NFS normal")

        # Patient 2 tente d'accéder au document de Patient 1 : Refusé (403)
        self.client.force_authenticate(user=self.other_patient_user)
        res_p2 = self.client.get(f"/documents_medicaux/{doc.id_document}/download/")
        self.assertEqual(res_p2.status_code, status.HTTP_403_FORBIDDEN)
