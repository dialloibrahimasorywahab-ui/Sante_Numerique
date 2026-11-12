import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentMedicalService } from '../../../../core/services/document-medical.service';
import { DocumentMedicalDto, CategorieDocument } from '../../../../core/models/document-medical.models';
import { DoctorService } from '../../services/doctor.service';
import { DoctorPatientDto } from '../../models/doctor.models';
import { formatDate as formatSharedDate } from '../../../../shared/utils';

@Component({
  selector: 'app-doctor-documents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-documents.component.html',
  styleUrl: './doctor-documents.component.scss'
})
export class DoctorDocumentsComponent implements OnInit {
  documentService = inject(DocumentMedicalService);
  doctorService = inject(DoctorService);

  searchQuery = signal<string>('');
  selectedCategory = signal<string>('');
  isUploadModalOpen = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  uploadSuccessMessage = signal<string | null>(null);
  uploadErrorMessage = signal<string | null>(null);
  decryptingDocId = signal<number | null>(null);

  patientsList = signal<DoctorPatientDto[]>([]);
  isLoadingPatients = signal<boolean>(false);

  // Formulaire d'upload praticien
  selectedPatientId: number | null = null;
  newDocTitle = '';
  newDocCategorie: CategorieDocument = 'RADIO';
  newDocDate = new Date().toISOString().split('T')[0];
  newDocObservation = '';
  selectedFile: File | null = null;

  ngOnInit(): void {
    this.loadDocuments();
    this.loadPatients();
  }

  loadDocuments(): void {
    this.documentService.getDocuments({
      categorie: this.selectedCategory(),
      search: this.searchQuery(),
      page: 1,
      page_size: 30
    }).subscribe();
  }

  loadPatients(): void {
    this.isLoadingPatients.set(true);
    this.doctorService.getPatients(1, '').subscribe({
      next: (res) => {
        this.patientsList.set(res.results || []);
        this.isLoadingPatients.set(false);
      },
      error: () => {
        this.isLoadingPatients.set(false);
      }
    });
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
    this.newDocCategorie = 'RADIO';
    this.newDocDate = new Date().toISOString().split('T')[0];
    this.newDocObservation = '';
    this.selectedFile = null;
    if (this.patientsList().length > 0 && !this.selectedPatientId) {
      this.selectedPatientId = this.patientsList()[0].id_patient;
    }
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
    if (!this.selectedPatientId) {
      this.uploadErrorMessage.set('Veuillez sélectionner un patient.');
      return;
    }
    if (!this.selectedFile || !this.newDocTitle.trim()) {
      this.uploadErrorMessage.set('Veuillez renseigner un intitulé et choisir un fichier.');
      return;
    }

    this.isSubmitting.set(true);
    this.uploadErrorMessage.set(null);

    const formData = new FormData();
    formData.append('patient', this.selectedPatientId.toString());
    formData.append('titre', this.newDocTitle.trim());
    formData.append('categorie', this.newDocCategorie);
    formData.append('date_document', this.newDocDate);
    formData.append('observation', this.newDocObservation);
    formData.append('fichier', this.selectedFile);

    this.documentService.uploadDocument(formData).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.uploadSuccessMessage.set('Examen chiffré (AES-256) et enregistré au dossier patient avec succès.');
        setTimeout(() => {
          this.closeUploadModal();
        }, 1200);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.uploadErrorMessage.set(err?.error?.error || 'Erreur lors du versement du document.');
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

  deleteDocument(doc: DocumentMedicalDto): void {
    const docId = doc.idDocument || doc.id_document || (doc as any).id;
    if (!docId) return;
    if (confirm(`Confirmez-vous l'archivage du document "${doc.titre}" ?`)) {
      this.documentService.deleteDocument(docId, false).subscribe();
    }
  }

  formatDate(dateStr?: string): string {
    return formatSharedDate(dateStr);
  }

  formatSize(bytes?: number | null): string {
    return this.documentService.formatFileSize(bytes);
  }
}
