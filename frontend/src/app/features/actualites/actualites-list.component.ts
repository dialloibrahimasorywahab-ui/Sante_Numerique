import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ActualiteService } from '../../core/services/actualite.service';
import { Actualite, CategorieActualite } from '../../core/models/actualite.model';

@Component({
  selector: 'app-actualites-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './actualites-list.component.html',
  styleUrl: './actualites-list.component.scss'
})
export class ActualitesListComponent implements OnInit {
  actualiteService = inject(ActualiteService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  // Filtres
  searchQuery = signal<string>('');
  selectedCategorySlug = signal<string>('all');
  selectedOrdering = signal<string>('-date_publication');
  currentPage = signal<number>(1);
  pageSize = 9;

  // Toast de partage
  copiedArticleId = signal<number | null>(null);

  // Article à la une calculé
  featuredArticle = computed(() => {
    const list = this.actualiteService.actualites();
    if (!list.length) return null;
    const une = list.find(a => a.estALaUne);
    return une || list[0];
  });

  // Autres articles de la grille (excluant la une si on est sur la page 1 et sans recherche)
  gridArticles = computed(() => {
    const list = this.actualiteService.actualites();
    const une = this.featuredArticle();
    if (une && !this.searchQuery() && this.selectedCategorySlug() === 'all' && this.currentPage() === 1) {
      return list.filter(a => a.id !== une.id);
    }
    return list;
  });

  ngOnInit(): void {
    // Écouter les query params pour les filtres partagés par URL
    this.route.queryParams.subscribe(params => {
      if (params['categorie']) {
        this.selectedCategorySlug.set(params['categorie']);
      }
      if (params['search']) {
        this.searchQuery.set(params['search']);
      }
      if (params['page']) {
        this.currentPage.set(Number(params['page']) || 1);
      }
      this.loadCategories();
      this.loadArticles();
    });
  }

  loadCategories(): void {
    this.actualiteService.getCategories().subscribe();
  }

  loadArticles(): void {
    const params: any = {
      page: this.currentPage(),
      pageSize: this.pageSize,
      ordering: this.selectedOrdering()
    };

    if (this.searchQuery().trim()) {
      params.search = this.searchQuery().trim();
    }

    if (this.selectedCategorySlug() !== 'all') {
      params.categorie = this.selectedCategorySlug();
    }

    this.actualiteService.getActualites(params).subscribe();
  }

  onSearch(): void {
    this.currentPage.set(1);
    this.updateUrlParams();
    this.loadArticles();
  }

  clearSearch(): void {
    this.searchQuery.set('');
    this.currentPage.set(1);
    this.updateUrlParams();
    this.loadArticles();
  }

  onSelectCategory(slug: string): void {
    this.selectedCategorySlug.set(slug);
    this.currentPage.set(1);
    this.updateUrlParams();
    this.loadArticles();
  }

  onOrderingChange(ordering: string): void {
    this.selectedOrdering.set(ordering);
    this.currentPage.set(1);
    this.loadArticles();
  }

  goToPage(page: number): void {
    if (page < 1 || page > this.actualiteService.totalPages()) return;
    this.currentPage.set(page);
    this.updateUrlParams();
    this.loadArticles();
    window.scrollTo({ top: 350, behavior: 'smooth' });
  }

  private updateUrlParams(): void {
    const queryParams: any = {};
    if (this.selectedCategorySlug() !== 'all') {
      queryParams.categorie = this.selectedCategorySlug();
    }
    if (this.searchQuery().trim()) {
      queryParams.search = this.searchQuery().trim();
    }
    if (this.currentPage() > 1) {
      queryParams.page = this.currentPage();
    }
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      queryParamsHandling: 'merge',
      replaceUrl: true
    });
  }

  resetFilters(): void {
    this.searchQuery.set('');
    this.selectedCategorySlug.set('all');
    this.currentPage.set(1);
    this.updateUrlParams();
    this.loadArticles();
  }

  shareArticle(article: Actualite, event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault();

    const url = `${window.location.origin}/actualites/${article.slug || article.id}`;

    if (navigator.share) {
      navigator.share({
        title: article.titre,
        text: article.resume,
        url: url
      }).catch(() => {
        this.copyToClipboard(url, article.id);
      });
    } else {
      this.copyToClipboard(url, article.id);
    }
  }

  private copyToClipboard(text: string, articleId: number): void {
    navigator.clipboard.writeText(text).then(() => {
      this.copiedArticleId.set(articleId);
      setTimeout(() => {
        if (this.copiedArticleId() === articleId) {
          this.copiedArticleId.set(null);
        }
      }, 2500);
    });
  }

  formatDate(dateString?: string | null): string {
    if (!dateString) return 'Récemment';
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }).format(date);
    } catch {
      return 'Récemment';
    }
  }

  getBadgeClass(couleur?: string): string {
    switch (couleur) {
      case 'emerald':
        return 'badge-emerald';
      case 'blue':
        return 'badge-blue';
      case 'purple':
        return 'badge-purple';
      case 'amber':
        return 'badge-amber';
      case 'rose':
        return 'badge-rose';
      default:
        return 'badge-teal';
    }
  }
}

