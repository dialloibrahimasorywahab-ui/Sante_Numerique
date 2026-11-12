from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from patients.models import Patient
from medecin.models import Medecin
from consultation.models import Consultation


class DocumentMedical(models.Model):
    """
    Modèle central de la Gestion Électronique des Documents Médicaux (GED).
    Prend en charge l'imagerie médicale (Radiographies, Scanners, IRM, Échographies),
    les bilans de biologie médicale, analyses sanguines et comptes-rendus cliniques.
    Les fichiers sont chiffrés au repos (AES-256 Fernet) pour garantir la conformité HDS/RGPD.
    """

    class Categorie(models.TextChoices):
        RADIO = "RADIO", "Radiographie"
        SCANNER = "SCANNER", "Scanner / TDM"
        IRM = "IRM", "IRM (Imagerie par Résonance Magnétique)"
        ECHOGRAPHIE = "ECHOGRAPHIE", "Échographie"
        ANALYSE_SANG = "ANALYSE_SANG", "Bilan Sanguin / Biologie médicale"
        ORDONNANCE = "ORDONNANCE", "Ordonnance numérisée"
        CERTIFICAT = "CERTIFICAT", "Certificat médical"
        COMPTE_RENDU = "COMPTE_RENDU", "Compte-rendu opératoire / hospitalier"
        AUTRE = "AUTRE", "Autre document médical"

    id_document = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="documents_medicaux",
        db_column="id_patient",
        help_text="Patient titulaire du document médical"
    )

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_medicaux_emis",
        db_column="id_medecin",
        help_text="Médecin prescripteur, analyste ou ayant téléversé le document"
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_medicaux",
        db_column="id_consultation",
        help_text="Consultation clinique associée (optionnelle)"
    )

    titre = models.CharField(
        max_length=200,
        help_text="Intitulé du document (ex: Scanner thoracique injecté, Bilan NFS)"
    )

    categorie = models.CharField(
        max_length=50,
        choices=Categorie.choices,
        default=Categorie.AUTRE,
        help_text="Classification médicale du document"
    )

    fichier = models.FileField(
        upload_to="documents_medicaux/%Y/%m/",
        help_text="Fichier stocké au format chiffré"
    )

    nom_original = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom initial du fichier lors du téléversement"
    )

    taille_octets = models.BigIntegerField(
        default=0,
        help_text="Taille en octets du fichier original"
    )

    type_mime = models.CharField(
        max_length=100,
        default="application/octet-stream",
        help_text="Type MIME du fichier (ex: application/pdf, image/png, image/dicom)"
    )

    checksum_sha256 = models.CharField(
        max_length=64,
        blank=True,
        help_text="Empreinte cryptographique SHA-256 du contenu pour intégrité"
    )

    chiffre = models.BooleanField(
        default=True,
        help_text="Garantit que le contenu est chiffré au repos via AES-256"
    )

    date_document = models.DateField(
        default=timezone.localdate,
        help_text="Date de réalisation de l'acte ou examen médical"
    )

    date_upload = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de versement dans la GED"
    )

    observation = models.TextField(
        blank=True,
        null=True,
        help_text="Conclusions médicales, compte-rendu radiologique ou notes"
    )

    actif = models.BooleanField(
        default=True,
        help_text="Soft-delete : archivage logique"
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Document Médical"
        verbose_name_plural = "Documents Médicaux (GED)"
        ordering = ["-date_document", "-id_document"]

    def __str__(self):
        return f"{self.get_categorie_display()} - {self.titre} ({self.patient})"

    @property
    def id(self) -> int:
        return self.id_document

    # Propriétés de compatibilité camelCase pour l'API REST
    @property
    def idDocument(self) -> int:
        return self.id_document

    @property
    def nomOriginal(self) -> str:
        return self.nom_original

    @property
    def tailleOctets(self) -> int:
        return self.taille_octets

    @property
    def typeMime(self) -> str:
        return self.type_mime

    @property
    def checksumSha256(self) -> str:
        return self.checksum_sha256

    @property
    def dateDocument(self):
        return self.date_document

    @property
    def dateUpload(self):
        return self.date_upload
