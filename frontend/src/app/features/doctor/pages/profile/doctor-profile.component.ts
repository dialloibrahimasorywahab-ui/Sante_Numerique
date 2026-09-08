import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { AuthService } from '../../../../core/services/auth.service';
import { DoctorService } from '../../services/doctor.service';
import { DoctorProfileDto } from '../../models/doctor.models';

@Component({
  selector: 'app-doctor-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './doctor-profile.component.html',
  styleUrl: './doctor-profile.component.scss'
})
export class DoctorProfileComponent implements OnInit {
  authService = inject(AuthService);
  private doctorService = inject(DoctorService);
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);

  isLoading = signal<boolean>(true);
  isSavingProfile = signal<boolean>(false);
  isChangingPassword = signal<boolean>(false);

  profileSuccess = signal<string | null>(null);
  profileError = signal<string | null>(null);

  passwordSuccess = signal<string | null>(null);
  passwordError = signal<string | null>(null);

  doctorProfile = signal<DoctorProfileDto | null>(null);

  profileForm!: FormGroup;
  passwordForm!: FormGroup;

  ngOnInit(): void {
    this.initForms();
    this.loadProfile();
  }

  private initForms(): void {
    this.profileForm = this.fb.group({
      telephonePro: ['', [Validators.required]],
      emailPro: ['', [Validators.email]],
      bureau: ['']
    });

    this.passwordForm = this.fb.group({
      ancienMotDePasse: ['', [Validators.required]],
      nouveauMotDePasse: ['', [Validators.required, Validators.minLength(8)]],
      confirmationMotDePasse: ['', [Validators.required]]
    });
  }

  private loadProfile(): void {
    this.isLoading.set(true);
    this.doctorService.getMyDoctorProfile().subscribe({
      next: (profile) => {
        if (profile) {
          this.doctorProfile.set(profile);
          this.profileForm.patchValue({
            telephonePro: profile.telephonePro || profile.telephone || '',
            emailPro: profile.emailPro || profile.email || '',
            bureau: profile.bureau || ''
          });
        }
        this.isLoading.set(false);
      },
      error: () => {
        this.profileError.set('Impossible de charger les données du profil.');
        this.isLoading.set(false);
      }
    });
  }

  onSubmitProfile(): void {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    const doc = this.doctorProfile();
    if (!doc) return;

    this.isSavingProfile.set(true);
    this.profileSuccess.set(null);
    this.profileError.set(null);

    const fVal = this.profileForm.value;

    this.doctorService.updateDoctorProfile(doc.idMedecin, {
      telephonePro: fVal.telephonePro,
      emailPro: fVal.emailPro,
      bureau: fVal.bureau
    }).subscribe({
      next: (updated) => {
        this.doctorProfile.set(updated);
        this.isSavingProfile.set(false);
        this.profileSuccess.set('Coordonnées professionnelles mises à jour avec succès.');
        setTimeout(() => this.profileSuccess.set(null), 3500);
      },
      error: (err) => {
        this.isSavingProfile.set(false);
        this.profileError.set(err?.error?.error || 'Erreur lors de la mise à jour des coordonnées.');
      }
    });
  }

  onSubmitPassword(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    const { ancienMotDePasse, nouveauMotDePasse, confirmationMotDePasse } = this.passwordForm.value;

    if (nouveauMotDePasse !== confirmationMotDePasse) {
      this.passwordError.set('Le nouveau mot de passe et sa confirmation ne correspondent pas.');
      return;
    }

    this.isChangingPassword.set(true);
    this.passwordSuccess.set(null);
    this.passwordError.set(null);

    this.http.post(`${environment.apiUrl}/users/change-password/`, {
      ancienMotDePasse,
      nouveauMotDePasse,
      confirmationMotDePasse
    }, { withCredentials: true }).subscribe({
      next: () => {
        this.isChangingPassword.set(false);
        this.passwordSuccess.set('Votre mot de passe a été modifié avec succès.');
        this.passwordForm.reset();
        setTimeout(() => this.passwordSuccess.set(null), 4000);
      },
      error: (err) => {
        this.isChangingPassword.set(false);
        this.passwordError.set(
          err?.error?.message || err?.error?.ancienMotDePasse?.[0] || 'Erreur lors du changement de mot de passe.'
        );
      }
    });
  }
}
