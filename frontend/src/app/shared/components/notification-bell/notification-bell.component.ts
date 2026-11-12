import { Component, inject, signal, computed, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { NotificationService } from '../../../core/services/notification.service';
import { AuthService } from '../../../core/services/auth.service';
import { NotificationHospitaliereDto, LiveAlertToast } from '../../../core/models/notification.models';

@Component({
  selector: 'app-notification-bell',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './notification-bell.component.html',
  styleUrl: './notification-bell.component.scss'
})
export class NotificationBellComponent {
  notificationService = inject(NotificationService);
  authService = inject(AuthService);
  private elementRef = inject(ElementRef);
  private router = inject(Router);

  isOpen = signal<boolean>(false);
  activeFilter = signal<string>('TOUS');

  isPatient = computed(() => this.authService.currentUser()?.role === 'PATIENT');

  rdvCount = computed(() =>
    this.notificationService.notifications().filter(n => n.type_notification === 'RAPPEL_RDV' || n.type_notification === 'NOUVEAU_RDV').length
  );

  medicamentCount = computed(() =>
    this.notificationService.notifications().filter(n => n.type_notification === 'PRISE_MEDICAMENT').length
  );

  get filteredNotifications(): NotificationHospitaliereDto[] {
    const list = this.notificationService.notifications();
    const filter = this.activeFilter();

    if (this.isPatient()) {
      if (filter === 'TOUS') return list;
      if (filter === 'RDV') return list.filter(n => n.type_notification === 'RAPPEL_RDV' || n.type_notification === 'NOUVEAU_RDV');
      if (filter === 'TRAITEMENT') return list.filter(n => n.type_notification === 'PRISE_MEDICAMENT');
      return list;
    } else {
      if (filter === 'TOUS') return list;
      if (filter === 'LIT_URGENCE') return list.filter(n => n.type_notification === 'LIT_URGENCE');
      if (filter === 'PATIENT_ARRIVE') return list.filter(n => n.type_notification === 'PATIENT_ARRIVE');
      return list;
    }
  }

  toggleDropdown(): void {
    this.isOpen.update(v => !v);
  }

  closeDropdown(): void {
    this.isOpen.set(false);
  }

  setFilter(filter: string): void {
    this.activeFilter.set(filter);
  }

  onMarkAsRead(notif: NotificationHospitaliereDto, event: Event): void {
    event.stopPropagation();
    if (!notif.lu) {
      this.notificationService.markAsRead(notif.id_notification).subscribe();
    }
  }

  onMarkAllAsRead(event: Event): void {
    event.stopPropagation();
    this.notificationService.markAllAsRead().subscribe();
  }

  dismissToast(toast: LiveAlertToast, event: Event): void {
    event.stopPropagation();
    this.notificationService.dismissToast(toast.id);
  }

  navigateToTarget(notif: NotificationHospitaliereDto): void {
    this.closeDropdown();
    if (this.isPatient()) {
      if (notif.type_notification === 'RAPPEL_RDV' || notif.type_notification === 'NOUVEAU_RDV') {
        this.router.navigate(['/patient/appointments']);
      } else if (notif.type_notification === 'PRISE_MEDICAMENT') {
        this.router.navigate(['/patient/prescriptions']);
      }
    }
  }

  // Fermeture du dropdown si clic à l'extérieur
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.elementRef.nativeElement.contains(event.target)) {
      this.closeDropdown();
    }
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      const today = new Date();
      if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
    } catch {
      return dateStr;
    }
  }
}
