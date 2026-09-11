import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { PatientProfileService } from '../../services/patient-profile.service';
import { calculateAge as calculateSharedAge } from '../../../../shared/utils';
import { AuthService } from '../../../../core/services/auth.service';
import { User } from '../../../../core/models/user.model';
import { PatientRecord, UpdateProfileDto } from '../../models/patient.models';

@Component({
  selector: 'app-patient-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './patient-profile.component.html',
  styleUrl: './patient-profile.component.scss'
})
export class PatientProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private profileService = inject(PatientProfileService);
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);

  currentUser = signal<User | null>(null);
  patientRecord = signal<PatientRecord | null>(null);

  isLoading = signal<boolean>(true);
  isSavingProfile = signal<boolean>(false);
  isChangingPassword = signal<boolean>(false);

  profileSuccessMessage = signal<string | null>(null);
  profileErrorMessage = signal<string | null>(null);

  passwordSuccessMessage = signal<string | null>(null);
  passwordErrorMessage = signal<string | null>(null);

  profileForm!: FormGroup;
  passwordForm!: FormGroup;

  activeTab = signal<'INFO' | 'EDIT' | 'PASSWORD'>('INFO');

  selectedDateNaissance = signal<string>('');

  // Âge calculé dynamiquement
  calculatedAge = computed<number | null>(() => {
    const bday = this.selectedDateNaissance() || this.profileForm?.get('date_naissance')?.value || this.currentUser()?.date_naissance || (this.currentUser() as any)?.dateNaissance || this.patientRecord()?.date_naissance;
    if (!bday) return null;
    const age = calculateSharedAge(bday, '');
    return typeof age === 'number' && age >= 0 ? age : null;
  });

  ngOnInit(): void {
    this.initForms();
    this.loadUserData();
    this.route.queryParams.subscribe(params => {
      if (params['tab'] === 'EDIT') {
        this.activeTab.set('EDIT');
      } else if (params['tab'] === 'PASSWORD') {
        this.activeTab.set('PASSWORD');
      }
    });
  }

  private initForms(): void {
    this.profileForm = this.fb.group({
      nom: ['', [Validators.required, Validators.minLength(2)]],
      prenom: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telephone: ['', [Validators.required, Validators.pattern(/^[0-9+\s-]{8,15}$/)]],
      date_naissance: [''],
      sexe: [''],
      adresse: [''],
      groupe_sanguin: [''],
      numero_securite_sociale: [''],
      personne_a_contacter: ['']
    });

    this.profileForm.get('date_naissance')?.valueChanges.subscribe(v => {
      this.selectedDateNaissance.set(v || '');
    });

    this.passwordForm = this.fb.group({
      ancienMotDePasse: ['', [Validators.required]],
      nouveauMotDePasse: ['', [Validators.required, Validators.minLength(6)]],
      confirmationMotDePasse: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  private passwordMatchValidator(group: FormGroup) {
    const nouveau = group.get('nouveauMotDePasse')?.value;
    const confirm = group.get('confirmationMotDePasse')?.value;
    return nouveau === confirm ? null : { mismatch: true };
  }

  loadUserData(): void {
    this.isLoading.set(true);

    this.profileService.getProfile().subscribe({
      next: (user) => {
        this.currentUser.set(user);
        this.profileForm.patchValue({
          nom: user.nom,
          prenom: user.prenom,
          email: user.email,
          telephone: user.telephone,
          date_naissance: user.date_naissance || user.dateNaissance || ''
        });

        // Tenter de charger la fiche médicale si patientId existe
        const patientId = (user as any).patient_id || user.id_user || user.idUser;
        if (patientId) {
          this.profileService.getPatientRecord(patientId).subscribe({
            next: (rec) => {
              this.patientRecord.set(rec);
              if (rec) {
                this.profileForm.patchValue({
                  sexe: rec.sexe || '',
                  adresse: rec.adresse || '',
                  groupe_sanguin: rec.groupe_sanguin || (rec as any).groupeSanguin || '',
                  numero_securite_sociale: rec.numero_securite_sociale || (rec as any).numeroSecuriteSociale || '',
                  personne_a_contacter: rec.personne_a_contacter || (rec as any).personneAContacter || '',
                  date_naissance: this.profileForm.get('date_naissance')?.value || rec.date_naissance || (rec as any).dateNaissance || ''
                });
                this.selectedDateNaissance.set(this.profileForm.get('date_naissance')?.value || '');
              }
            }
          });
        }
        this.isLoading.set(false);
      },
      error: () => {
        // Fallback sur le signal de l'authService
        const cached = this.authService.currentUser();
        if (cached) {
          this.currentUser.set(cached);
          this.profileForm.patchValue({
            nom: cached.nom,
            prenom: cached.prenom,
            email: cached.email,
            telephone: cached.telephone,
            date_naissance: cached.date_naissance || cached.dateNaissance || ''
          });
          this.selectedDateNaissance.set(cached.date_naissance || cached.dateNaissance || '');
        }
        this.isLoading.set(false);
      }
    });
  }

  setTab(tab: 'INFO' | 'EDIT' | 'PASSWORD'): void {
    this.activeTab.set(tab);
    this.profileSuccessMessage.set(null);
    this.profileErrorMessage.set(null);
    this.passwordSuccessMessage.set(null);
    this.passwordErrorMessage.set(null);
  }

  submitProfileUpdate(): void {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    const user = this.currentUser();
    if (!user) return;

    this.isSavingProfile.set(true);
    this.profileErrorMessage.set(null);
    this.profileSuccessMessage.set(null);

    const userId = user.id_user || user.idUser || 0;
    const formVal = this.profileForm.value;

    const userPayload: UpdateProfileDto = {
      nom: formVal.nom,
      prenom: formVal.prenom,
      email: formVal.email,
      telephone: formVal.telephone,
      date_naissance: formVal.date_naissance || null
    };

    const patientId = (user as any).patient_id || user.id_user || user.idUser;

    this.profileService.updateProfile(userId, userPayload).subscribe({
      next: (updatedUser) => {
        this.currentUser.set(updatedUser);
        this.authService.updateCurrentUser(updatedUser);

        // Sauvegarder également les coordonnées et données médicales
        if (patientId) {
          this.profileService.updatePatientRecord(patientId, {
            sexe: formVal.sexe,
            adresse: formVal.adresse,
            groupe_sanguin: formVal.groupe_sanguin,
            numero_securite_sociale: formVal.numero_securite_sociale,
            personne_a_contacter: formVal.personne_a_contacter,
            date_naissance: formVal.date_naissance || null
          }).subscribe({
            next: (updatedRecord) => {
              this.patientRecord.set(updatedRecord);
              this.isSavingProfile.set(false);
              this.profileSuccessMessage.set('Vos informations personnelles, votre âge et vos données médicales ont été enregistrés avec succès.');
              setTimeout(() => this.profileSuccessMessage.set(null), 5000);
            },
            error: () => {
              this.isSavingProfile.set(false);
              this.profileSuccessMessage.set('Vos coordonnées principales ont été mises à jour.');
              setTimeout(() => this.profileSuccessMessage.set(null), 5000);
            }
          });
        } else {
          this.isSavingProfile.set(false);
          this.profileSuccessMessage.set('Vos informations ont été mises à jour avec succès.');
          setTimeout(() => this.profileSuccessMessage.set(null), 5000);
        }
      },
      error: (err) => {
        this.isSavingProfile.set(false);
        const detail = err?.error?.message || err?.error?.error || 'Erreur lors de la mise à jour de votre profil.';
        this.profileErrorMessage.set(detail);
      }
    });
  }

  submitPasswordChange(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.isChangingPassword.set(true);
    this.passwordErrorMessage.set(null);
    this.passwordSuccessMessage.set(null);

    const val = this.passwordForm.value;

    this.profileService.changePassword({
      ancienMotDePasse: val.ancienMotDePasse,
      nouveauMotDePasse: val.nouveauMotDePasse,
      confirmationMotDePasse: val.confirmationMotDePasse
    }).subscribe({
      next: () => {
        this.isChangingPassword.set(false);
        this.passwordSuccessMessage.set('Votre mot de passe a été modifié avec succès.');
        this.passwordForm.reset();
        setTimeout(() => this.passwordSuccessMessage.set(null), 5000);
      },
      error: (err) => {
        this.isChangingPassword.set(false);
        const detail = err?.error?.message || err?.error?.error || 'Échec de la modification du mot de passe. Vérifiez votre mot de passe actuel.';
        this.passwordErrorMessage.set(detail);
      }
    });
  }
}
