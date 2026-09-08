import { Component, output, inject, computed } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map, startWith } from 'rxjs';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';

@Component({
  selector: 'app-public-layout',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  template: `
    @if (showHeaderFooter()) {
      <app-header
        (openBookingModal)="openBookingModal.emit()"
        (openPrescriptionModal)="openPrescriptionModal.emit()"
        (scrollToSection)="scrollToSection.emit($event)">
      </app-header>
    }
    <main>
      <router-outlet></router-outlet>
    </main>
    @if (showHeaderFooter()) {
      <app-footer
        (scrollToSection)="scrollToSection.emit($event)">
      </app-footer>
    }
  `
})
export class PublicLayoutComponent {
  private router = inject(Router);

  openBookingModal = output<void>();
  openPrescriptionModal = output<void>();
  scrollToSection = output<string>();

  private currentUrl = toSignal(
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(event => (event as NavigationEnd).urlAfterRedirects || (event as NavigationEnd).url),
      startWith(this.router.url)
    ),
    { initialValue: this.router.url }
  );

  showHeaderFooter = computed(() => {
    const raw = this.currentUrl() || '';
    const cleanUrl = raw.split('?')[0].split('#')[0].toLowerCase().trim();
    if (cleanUrl === '/login' || cleanUrl === '/register') return false;
    if (cleanUrl.startsWith('/patient') || cleanUrl.startsWith('/admin') || cleanUrl.startsWith('/medecin')) return false;
    return true;
  });
}
