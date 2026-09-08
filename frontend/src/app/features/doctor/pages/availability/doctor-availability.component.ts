import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../services/doctor.service';
import {
  DisponibiliteMedecinDto,
  IndisponibiliteMedecinDto,
  DoctorProfileDto,
  CreneauxResponseDto
} from '../../models/doctor.models';

interface DayScheduleModel {
  jour_semaine: number;
  label: string;
  actif: boolean;
  heure_debut: string;
  heure_fin: string;
  pause_debut: string;
  pause_fin: string;
  duree_creneau: number;
}

@Component({
  selector: 'app-doctor-availability',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor-availability.component.html',
  styleUrl: './doctor-availability.component.scss'
})
export class DoctorAvailabilityComponent implements OnInit {
  private doctorService = inject(DoctorService);

  activeTab = signal<'CRENEAUX' | 'INDISPONIBILITES'>('CRENEAUX');

  isLoading = signal<boolean>(true);
  isSaving = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  doctorProfile = signal<DoctorProfileDto | null>(null);

  // Weekly Schedule Array (Monday to Sunday)
  weeklySchedule = signal<DayScheduleModel[]>([
    { jour_semaine: 0, label: 'Lundi', actif: true, heure_debut: '08:30', heure_fin: '16:30', pause_debut: '12:30', pause_fin: '14:00', duree_creneau: 45 },
    { jour_semaine: 1, label: 'Mardi', actif: true, heure_debut: '08:30', heure_fin: '16:30', pause_debut: '12:30', pause_fin: '14:00', duree_creneau: 45 },
    { jour_semaine: 2, label: 'Mercredi', actif: true, heure_debut: '08:30', heure_fin: '16:30', pause_debut: '12:30', pause_fin: '14:00', duree_creneau: 45 },
    { jour_semaine: 3, label: 'Jeudi', actif: true, heure_debut: '08:30', heure_fin: '16:30', pause_debut: '12:30', pause_fin: '14:00', duree_creneau: 45 },
    { jour_semaine: 4, label: 'Vendredi', actif: true, heure_debut: '08:30', heure_fin: '16:30', pause_debut: '12:30', pause_fin: '14:00', duree_creneau: 45 },
    { jour_semaine: 5, label: 'Samedi', actif: false, heure_debut: '09:00', heure_fin: '13:00', pause_debut: '', pause_fin: '', duree_creneau: 45 },
    { jour_semaine: 6, label: 'Dimanche', actif: false, heure_debut: '09:00', heure_fin: '13:00', pause_debut: '', pause_fin: '', duree_creneau: 45 }
  ]);

  // Unavailabilities
  unavailabilities = signal<IndisponibiliteMedecinDto[]>([]);

  // New Unavailability Form Model
  newIndispo = {
    date_debut: new Date().toISOString().split('T')[0],
    date_fin: new Date().toISOString().split('T')[0],
    toute_la_journee: true,
    heure_debut: '08:30',
    heure_fin: '16:30',
    motif: 'Congé annuel'
  };

  // Preview Slots State
  previewDate = signal<string>(new Date().toISOString().split('T')[0]);
  previewSlots = signal<CreneauxResponseDto | null>(null);

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.doctorService.getMyDoctorProfile().subscribe({
      next: (profile) => {
        this.doctorProfile.set(profile);

        // Load existing availabilities
        this.doctorService.getAvailabilities().subscribe({
          next: (dispos) => {
            if (dispos && dispos.length > 0) {
              const updated = this.weeklySchedule().map(day => {
                const found = dispos.find(d => (d.jour_semaine ?? d.jourSemaine) === day.jour_semaine);
                if (found) {
                  return {
                    ...day,
                    actif: found.actif,
                    heure_debut: (found.heure_debut || found.heureDebut || '08:30').slice(0, 5),
                    heure_fin: (found.heure_fin || found.heureFin || '16:30').slice(0, 5),
                    pause_debut: (found.pause_debut || found.pauseDebut || '').slice(0, 5),
                    pause_fin: (found.pause_fin || found.pauseFin || '').slice(0, 5),
                    duree_creneau: found.duree_creneau || found.dureeCreneau || 45
                  };
                }
                return day;
              });
              this.weeklySchedule.set(updated);
            }

            // Load unavailabilities
            this.doctorService.getUnavailabilities().subscribe({
              next: (indispos) => {
                this.unavailabilities.set(indispos || []);
                this.isLoading.set(false);
                this.loadPreview();
              },
              error: () => {
                this.isLoading.set(false);
              }
            });
          },
          error: () => {
            this.isLoading.set(false);
          }
        });
      },
      error: () => {
        this.errorMessage.set('Impossible de charger les données de disponibilité.');
        this.isLoading.set(false);
      }
    });
  }

  saveWeeklySchedule(): void {
    this.isSaving.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const payload = this.weeklySchedule().map(day => ({
      jour_semaine: day.jour_semaine,
      heure_debut: day.heure_debut,
      heure_fin: day.heure_fin,
      pause_debut: day.pause_debut || null,
      pause_fin: day.pause_fin || null,
      duree_creneau: day.duree_creneau,
      actif: day.actif
    }));

    this.doctorService.saveBulkAvailabilities(payload).subscribe({
      next: () => {
        this.isSaving.set(false);
        this.successMessage.set('Planning hebdomadaire mis à jour avec succès.');
        this.loadPreview();
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(this.getApiErrorMessage(err, 'Erreur lors de l’enregistrement des créneaux.'));
      }
    });
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const payload = error?.error;
    if (typeof payload === 'string') return payload;
    if (payload?.error) return payload.error;
    if (payload && typeof payload === 'object') {
      const details = Object.entries(payload)
        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
        .join(' | ');
      if (details) return details;
    }
    return fallback;
  }

  addUnavailability(): void {
    if (!this.newIndispo.date_debut || !this.newIndispo.date_fin) {
      this.errorMessage.set('Veuillez renseigner les dates de début et de fin.');
      return;
    }

    this.isSaving.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const payload: Partial<IndisponibiliteMedecinDto> = {
      date_debut: this.newIndispo.date_debut,
      date_fin: this.newIndispo.date_fin,
      toute_la_journee: this.newIndispo.toute_la_journee,
      heure_debut: this.newIndispo.toute_la_journee ? null : this.newIndispo.heure_debut,
      heure_fin: this.newIndispo.toute_la_journee ? null : this.newIndispo.heure_fin,
      motif: this.newIndispo.motif,
      actif: true
    };

    this.doctorService.createUnavailability(payload).subscribe({
      next: (created) => {
        this.unavailabilities.update(list => [created, ...list]);
        this.isSaving.set(false);
        this.successMessage.set('Indisponibilité enregistrée avec succès.');
        this.loadPreview();
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(this.getApiErrorMessage(err, 'Erreur lors de l’enregistrement de l’indisponibilité.'));
      }
    });
  }

  deleteUnavailability(id?: number): void {
    if (!id) return;
    this.doctorService.deleteUnavailability(id).subscribe({
      next: () => {
        this.unavailabilities.update(list => list.filter(item => item.id !== id));
        this.loadPreview();
      }
    });
  }

  loadPreview(): void {
    const doc = this.doctorProfile();
    if (!doc) return;

    this.doctorService.getDoctorSlots(this.previewDate(), doc.idMedecin).subscribe({
      next: (res) => {
        this.previewSlots.set(res);
      }
    });
  }

  onPreviewDateChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.previewDate.set(input.value);
    this.loadPreview();
  }
}
