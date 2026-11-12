import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ActualiteService } from '../../../../core/services/actualite.service';
import { Actualite, CategorieActualite, StatutActualite } from '../../../../core/models/actualite.model';

@Component({
  selector: 'app-admin-actualites',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './admin-actualites.component.html',
  styleUrl: './admin-actualites.component.scss'
})
export class AdminActualitesComponent implements OnInit {
  actualiteService = inject(ActualiteService);
  private fb = inject(FormBuilder);

  // Liste et filtres
  articles = signal<Actualite[]>([]);
  categories = signal<CategorieActualite[]>([]);
  isLoading = signal<boolean>(false);
  filterSearch = signal<string>('');
  filterStatut = signal<string>('ALL');
  filterCategorie = signal<string>('ALL');

  // Modal d'édition/création
  isModalOpen = signal<boolean>(false);
  isSubmitting = signal<boolean>(false);
  modalMode = signal<'CREATE' | 'EDIT'>('CREATE');
  editingArticleId = signal<number | null>(null);
  selectedFile: File | null = null;
  imagePreview = signal<string | null>(null);

  // Modal de confirmation de suppression
  isDeleteModalOpen = signal<boolean>(false);
  articleToDelete = signal<Actualite | null>(null);

  // Toast de feedback
  toastMessage = signal<string | null>(null);

  // Formulaire réactif
  articleForm: FormGroup = this.fb.group({
    titre: ['', [Validators.required, Validators.minLength(5)]],
    categorie: ['', [Validators.required]],
    resume: ['', [Validators.required, Validators.minLength(10)]],
    contenu: ['', [Validators.required, Validators.minLength(20)]],
    imageUrl: [''],
    statut: ['BROUILLON', [Validators.required]],
    estALaUne: [false]
  });

  // Statistiques calculées
  stats = computed(() => {
    const list = this.articles();
    const total = list.length;
    const publies = list.filter(a => a.statut === 'PUBLIE').length;
    const brouillons = list.filter(a => a.statut === 'BROUILLON').length;
    const totalVues = list.reduce((sum, a) => sum + (a.vues || 0), 0);
    return { total, publies, brouillons, totalVues };
  });

  // Liste filtrée côté client pour réactivité instantanée
  filteredArticles = computed(() => {
    let list = this.articles();
    const search = this.filterSearch().toLowerCase().trim();
    const statut = this.filterStatut();
    const cat = this.filterCategorie();

    if (search) {
      list = list.filter(a =>
        a.titre.toLowerCase().includes(search) ||
        a.resume.toLowerCase().includes(search)
      );
    }

    if (statut !== 'ALL') {
      list = list.filter(a => a.statut === statut);
    }

    if (cat !== 'ALL') {
      list = list.filter(a => a.categorie === Number(cat) || a.categorieSlug === cat);
    }

    return list;
  });

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    // Les administrateurs chargent tous les articles sans restriction de statut
    this.actualiteService.getActualites({ pageSize: 100, ordering: '-date_creation' }).subscribe({
      next: (res) => {
        this.articles.set(res.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });

    this.actualiteService.getCategories().subscribe({
      next: (cats) => this.categories.set(cats)
    });
  }

  openCreateModal(): void {
    this.modalMode.set('CREATE');
    this.editingArticleId.set(null);
    this.selectedFile = null;
    this.imagePreview.set(null);
    this.articleForm.reset({
      titre: '',
      categorie: this.categories().length ? this.categories()[0].id : '',
      resume: '',
      contenu: '',
      imageUrl: '',
      statut: 'BROUILLON',
      estALaUne: false
    });
    this.isModalOpen.set(true);
  }

  openEditModal(article: Actualite): void {
    this.modalMode.set('EDIT');
    this.editingArticleId.set(article.id);
    this.selectedFile = null;
    this.imagePreview.set(article.image || null);
    this.articleForm.patchValue({
      titre: article.titre,
      categorie: article.categorie,
      resume: article.resume,
      contenu: article.contenu || '',
      imageUrl: article.imageUrl || '',
      statut: article.statut,
      estALaUne: article.estALaUne
    });
    this.isModalOpen.set(true);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.selectedFile = null;
    this.imagePreview.set(null);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview.set(e.target?.result as string);
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  submitArticle(): void {
    if (this.articleForm.invalid) {
      this.articleForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    const formVal = this.articleForm.value;

    const formData = new FormData();
    formData.append('titre', formVal.titre);
    formData.append('categorie', formVal.categorie);
    formData.append('resume', formVal.resume);
    formData.append('contenu', formVal.contenu);
    formData.append('statut', formVal.statut);
    formData.append('est_a_la_une', formVal.estALaUne ? 'true' : 'false');

    if (formVal.imageUrl) {
      formData.append('image_url', formVal.imageUrl);
    }

    if (this.selectedFile) {
      formData.append('image_couverture', this.selectedFile);
    }

    if (this.modalMode() === 'CREATE') {
      this.actualiteService.createActualite(formData).subscribe({
        next: (created) => {
          this.isSubmitting.set(false);
          this.closeModal();
          this.showToast('Article créé avec succès !');
          this.loadData();
        },
        error: (err) => {
          this.isSubmitting.set(false);
          console.error('Erreur création article:', err);
          this.showToast('Erreur lors de la création.');
        }
      });
    } else {
      const id = this.editingArticleId();
      if (!id) return;

      this.actualiteService.updateActualite(id, formData).subscribe({
        next: (updated) => {
          this.isSubmitting.set(false);
          this.closeModal();
          this.showToast('Article mis à jour avec succès !');
          this.loadData();
        },
        error: (err) => {
          this.isSubmitting.set(false);
          console.error('Erreur modification article:', err);
          this.showToast('Erreur lors de la mise à jour.');
        }
      });
    }
  }

  toggleStatut(article: Actualite, event: MouseEvent): void {
    event.stopPropagation();
    const newStatut: StatutActualite = article.statut === 'PUBLIE' ? 'BROUILLON' : 'PUBLIE';
    this.actualiteService.updateActualite(article.id, { statut: newStatut }).subscribe({
      next: () => {
        this.showToast(`Statut basculé en ${newStatut === 'PUBLIE' ? 'Publié' : 'Brouillon'}`);
        this.loadData();
      },
      error: () => this.showToast('Erreur lors du changement de statut.')
    });
  }

  toggleALaUne(article: Actualite, event: MouseEvent): void {
    event.stopPropagation();
    const newUne = !article.estALaUne;
    this.actualiteService.updateActualite(article.id, { estALaUne: newUne }).subscribe({
      next: () => {
        this.showToast(newUne ? 'Article mis à la une !' : 'Retiré de la une.');
        this.loadData();
      },
      error: () => this.showToast('Erreur lors du changement.')
    });
  }

  confirmDelete(article: Actualite, event: MouseEvent): void {
    event.stopPropagation();
    this.articleToDelete.set(article);
    this.isDeleteModalOpen.set(true);
  }

  closeDeleteModal(): void {
    this.isDeleteModalOpen.set(false);
    this.articleToDelete.set(null);
  }

  executeDelete(): void {
    const art = this.articleToDelete();
    if (!art) return;

    this.actualiteService.deleteActualite(art.id).subscribe({
      next: () => {
        this.closeDeleteModal();
        this.showToast('Article supprimé avec succès.');
        this.loadData();
      },
      error: () => {
        this.closeDeleteModal();
        this.showToast('Erreur lors de la suppression.');
      }
    });
  }

  showToast(msg: string): void {
    this.toastMessage.set(msg);
    setTimeout(() => this.toastMessage.set(null), 3000);
  }

  formatDate(dateString?: string | null): string {
    if (!dateString) return 'Non publié';
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }).format(date);
    } catch {
      return 'Non publié';
    }
  }
}

