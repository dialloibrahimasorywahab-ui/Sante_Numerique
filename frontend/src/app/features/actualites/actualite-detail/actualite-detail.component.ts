import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { ActualiteService } from '../../../core/services/actualite.service';
import { Actualite } from '../../../core/models/actualite.model';

@Component({
  selector: 'app-actualite-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './actualite-detail.component.html',
  styleUrl: './actualite-detail.component.scss'
})
export class ActualiteDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  actualiteService = inject(ActualiteService);

  article = signal<Actualite | null>(null);
  suggestions = signal<Actualite[]>([]);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string | null>(null);
  toastMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const slugOrId = params.get('slug') || params.get('id');
      if (slugOrId) {
        this.loadArticle(slugOrId);
      }
    });
  }

  loadArticle(slugOrId: string): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });

    this.actualiteService.getActualiteBySlugOrId(slugOrId).subscribe({
      next: (art) => {
        this.article.set(art);
        this.isLoading.set(false);
        this.loadSuggestions(art.slug || art.id);
      },
      error: () => {
        this.isLoading.set(false);
        this.errorMessage.set('Cet article est introuvable ou a été dépublié.');
      }
    });
  }

  loadSuggestions(slugOrId: string | number): void {
    this.actualiteService.getSuggestions(slugOrId).subscribe({
      next: (items) => this.suggestions.set(items),
      error: () => this.suggestions.set([])
    });
  }

  shareArticle(channel?: string): void {
    const art = this.article();
    if (!art) return;

    const url = window.location.href;
    const title = art.titre;

    if (!channel && navigator.share) {
      navigator.share({
        title,
        text: art.resume,
        url
      }).catch(() => this.copyToClipboard(url));
      return;
    }

    switch (channel) {
      case 'whatsapp':
        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' - ' + url)}`, '_blank');
        break;
      case 'facebook':
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
        break;
      case 'twitter':
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`, '_blank');
        break;
      case 'linkedin':
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
        break;
      default:
        this.copyToClipboard(url);
    }
  }

  copyToClipboard(url?: string): void {
    const targetUrl = url || window.location.href;
    navigator.clipboard.writeText(targetUrl).then(() => {
      this.toastMessage.set('Lien de l’article copié dans le presse-papier !');
      setTimeout(() => this.toastMessage.set(null), 3000);
    });
  }

  formatDate(dateString?: string | null): string {
    if (!dateString) return 'Récemment';
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      }).format(date);
    } catch {
      return 'Récemment';
    }
  }

  getBadgeClass(couleur?: string): string {
    switch (couleur) {
      case 'emerald': return 'badge-emerald';
      case 'blue': return 'badge-blue';
      case 'purple': return 'badge-purple';
      case 'amber': return 'badge-amber';
      case 'rose': return 'badge-rose';
      default: return 'badge-teal';
    }
  }
}

