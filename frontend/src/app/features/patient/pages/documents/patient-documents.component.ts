import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentMedicalService, CategorieOption } from '../../../../core/services/document-medical.service';
import { DocumentMedicalDto, CategorieDocument } from '../../../../core/models/document-medical.models';
import { AuthService } from '../../../../core/services/auth.service';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-patient-documents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './patient-documents.component.html',
  styleUrl: './patient-documents.component.scss'
})
export class PatientDocumentsComponent implements OnInit {
  documentService = inject(DocumentMedicalService);
  authService = inject(AuthService);

  searchQuery = signal<string>('');
  selectedCategory = signal<string>('');
  isUploadModalOpen = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  uploadSuccessMessage = signal<string | null>(null);
  uploadErrorMessage = signal<string | null>(null);
  decryptingDocId = signal<number | null>(null);

  // Formulaire d'upload
  newDocTitle = '';
  newDocCategorie: CategorieDocument = 'ANALYSE_SANG';
  newDocDate = new Date().toISOString().split('T')[0];
  newDocObservation = '';
  selectedFile: File | null = null;

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.documentService.getDocuments({
      categorie: this.selectedCategory(),
      search: this.searchQuery(),
      page: 1,
      page_size: 20
    }).subscribe();
  }

  onCategorySelect(catCode: string): void {
    this.selectedCategory.set(catCode);
    this.loadDocuments();
  }

  onSearchChange(): void {
    this.loadDocuments();
  }

  openUploadModal(): void {
    this.uploadSuccessMessage.set(null);
    this.uploadErrorMessage.set(null);
    this.newDocTitle = '';
    this.newDocCategorie = 'ANALYSE_SANG';
    this.newDocDate = new Date().toISOString().split('T')[0];
    this.newDocObservation = '';
    this.selectedFile = null;
    this.isUploadModalOpen.set(true);
  }

  closeUploadModal(): void {
    this.isUploadModalOpen.set(false);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      if (!this.newDocTitle) {
        this.newDocTitle = this.selectedFile.name.replace(/\.[^/.]+$/, '');
      }
    }
  }

  onSubmitUpload(): void {
    if (!this.selectedFile || !this.newDocTitle.trim()) {
      this.uploadErrorMessage.set('Veuillez renseigner un titre et sélectionner un fichier.');
      return;
    }

    const currentPatient = this.authService.currentUser();
    const patientId = (currentPatient as any)?.id_patient || (currentPatient as any)?.patient_id || currentPatient?.id_user || currentPatient?.idUser;
    if (!patientId) {
      this.uploadErrorMessage.set('Profil patient non trouvé.');
      return;
    }

    this.isSubmitting.set(true);
    this.uploadErrorMessage.set(null);

    const formData = new FormData();
    formData.append('patient', patientId.toString());
    formData.append('titre', this.newDocTitle.trim());
    formData.append('categorie', this.newDocCategorie);
    formData.append('date_document', this.newDocDate);
    formData.append('observation', this.newDocObservation);
    formData.append('fichier', this.selectedFile);

    this.documentService.uploadDocument(formData).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.uploadSuccessMessage.set('Document chiffré et téléversé avec succès dans votre dossier médical.');
        setTimeout(() => {
          this.closeUploadModal();
        }, 1200);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.uploadErrorMessage.set(err?.error?.error || 'Échec du téléversement du document.');
      }
    });
  }

  downloadDocument(doc: DocumentMedicalDto): void {
    const docId = doc.idDocument || doc.id_document || (doc as any).id;
    const filename = doc.nomOriginal || doc.nom_original || `${doc.titre}.pdf`;
    if (!docId) {
      console.error('Identifiant de document manquant', doc);
      return;
    }

    this.decryptingDocId.set(docId);
    this.documentService.downloadDecrypted(docId, filename).subscribe({
      next: () => {
        this.decryptingDocId.set(null);
      },
      error: (err) => {
        this.decryptingDocId.set(null);
        console.error('Erreur lors du déchiffrement du document:', err);
        alert('Erreur lors du déchiffrement du document.');
      }
    });
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }

  formatSize(bytes?: number | null): string {
    return this.documentService.formatFileSize(bytes);
  }
}
