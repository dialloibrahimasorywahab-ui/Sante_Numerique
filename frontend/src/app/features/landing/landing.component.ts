import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ActualiteService } from '../../core/services/actualite.service';
import { Actualite } from '../../core/models/actualite.model';

export interface DisplayActualite {
  id?: number | string;
  slug?: string;
  titre: string;
  resume: string;
  dateStr: string;
  imageUrl: string;
}

export interface ServiceCardItem {
  id: string;
  title: string;
  subtitle: string;
  icon: 'stethoscope' | 'bed' | 'calendar' | 'pill';
  route: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss'
})
export class HomeComponent implements OnInit {
  authService = inject(AuthService);
  private actualiteService = inject(ActualiteService);
  private router = inject(Router);

  // 4 Services Cards as seen on the reference mockup
  readonly servicesCards: ServiceCardItem[] = [
    {
      id: 'consultations',
      title: 'Consultations médicales',
      subtitle: 'Consultez nos spécialistes',
      icon: 'stethoscope',
      route: '/medecins'
    },
    {
      id: 'hospitalisation',
      title: 'Hospitalisation',
      subtitle: 'Des soins en toute sérénité',
      icon: 'bed',
      route: '/services'
    },
    {
      id: 'rendez-vous',
      title: 'Rendez-vous en ligne',
      subtitle: 'Prenez rendez-vous facilement',
      icon: 'calendar',
      route: '/rendez-vous'
    },
    {
      id: 'ordonnances',
      title: 'Ordonnances',
      subtitle: 'Vos prescriptions en ligne',
      icon: 'pill',
      route: '/services'
    }
  ];

  // 3 Mockup Reference News (Fallback if API is empty or offline)
  readonly defaultActualites: DisplayActualite[] = [
    {
      id: 1,
      slug: 'nouveau-service-cardiologie',
      titre: 'Nouveau service de cardiologie',
      resume: 'Notre hôpital ouvre un nouveau service de cardiologie pour mieux vous servir.',
      dateStr: '10 Nov. 2026',
      imageUrl: 'assets/actu_cardio.jpg'
    },
    {
      id: 2,
      slug: 'campagne-vaccination',
      titre: 'Campagne de vaccination',
      resume: 'Une campagne de vaccination est lancée dans notre établissement.',
      dateStr: '08 Nov. 2026',
      imageUrl: 'assets/actu_vaccin.jpg'
    },
    {
      id: 3,
      slug: 'nouvel-equipement-medical',
      titre: 'Nouvel équipement médical',
      resume: 'Un scanner de dernière génération désormais disponible.',
      dateStr: '05 Nov. 2026',
      imageUrl: 'assets/actu_equipement.jpg'
    }
  ];

  actualitesList = signal<DisplayActualite[]>(this.defaultActualites);

  ngOnInit(): void {
    this.loadRecentActualites();
  }

  private loadRecentActualites(): void {
    this.actualiteService.getActualites({
      pageSize: 3,
      ordering: '-date_publication',
      statut: 'PUBLIE'
    }).subscribe({
      next: (response) => {
        if (response && response.results && response.results.length > 0) {
          const mapped: DisplayActualite[] = response.results.slice(0, 3).map((actu: Actualite, index: number) => ({
            id: actu.id,
            slug: actu.slug,
            titre: actu.titre,
            resume: actu.resume || actu.contenu?.substring(0, 85) + '...',
            dateStr: this.formatDate(actu.datePublication || actu.dateCreation),
            imageUrl: actu.imageUrl || actu.imageCouverture || actu.image || this.defaultActualites[index % 3].imageUrl
          }));
          this.actualitesList.set(mapped);
        }
      },
      error: () => {
        // En cas d'erreur réseau / sandbox, on garde les 3 actualités conformes à la maquette
        this.actualitesList.set(this.defaultActualites);
      }
    });
  }

  private formatDate(dateStr?: string | null): string {
    if (!dateStr) return '10 Nov. 2026';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '10 Nov. 2026';
    
    const day = String(date.getDate()).padStart(2, '0');
    const months = ['Jan.', 'Fév.', 'Mar.', 'Avr.', 'Mai', 'Juin', 'Juil.', 'Août', 'Sep.', 'Oct.', 'Nov.', 'Déc.'];
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  }

  onServiceCardClick(card: ServiceCardItem): void {
    this.router.navigate([card.route]);
  }
}
