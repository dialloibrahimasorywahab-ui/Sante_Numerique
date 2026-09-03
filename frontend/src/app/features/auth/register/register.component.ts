import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { RegisterDto } from '../../../core/models/user.model';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  registerForm!: FormGroup;
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  showPassword = signal<boolean>(false);
  showConfirmPassword = signal<boolean>(false);

  ngOnInit(): void {
    this.initForm();
  }

  private initForm(): void {
    this.registerForm = this.fb.group({
      prenom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
      nom: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
      email: ['', [Validators.required, Validators.email, Validators.maxLength(150)]],
      telephone: ['', [Validators.required, Validators.pattern(/^[+]?[0-9\s-]{8,20}$/)]],
      login: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150), Validators.pattern(/^[a-zA-Z0-9_.-]+$/)]],
      motDePasse: ['', [Validators.required, Validators.minLength(8)]],
      confirmationMotDePasse: ['', [Validators.required]]
    }, {
      validators: [this.passwordMatchValidator]
    });
  }

  private passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('motDePasse')?.value;
    const confirmPassword = control.get('confirmationMotDePasse')?.value;

    if (password && confirmPassword && password !== confirmPassword) {
      control.get('confirmationMotDePasse')?.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    return null;
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(prev => !prev);
  }

  toggleConfirmPasswordVisibility(): void {
    this.showConfirmPassword.update(prev => !prev);
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const fv = this.registerForm.value;
    const payload: RegisterDto = {
      prenom: fv.prenom.trim(),
      nom: fv.nom.trim(),
      email: fv.email.trim().toLowerCase(),
      telephone: fv.telephone.trim(),
      login: fv.login.trim(),
      motDePasse: fv.motDePasse
    };

    this.authService.register(payload).subscribe({
      next: () => {
        this.isLoading.set(false);
        // Redirection vers /login avec paramètre pour message de bienvenue
        this.router.navigate(['/login'], {
          queryParams: { registered: 'true' }
        });
      },
      error: (err) => {
        this.isLoading.set(false);
        
        // Extraction précise des messages de validation renvoyés par DRF
        if (err?.error && typeof err.error === 'object') {
          const errors = err.error;
          if (errors.email) {
            this.errorMessage.set(`Adresse email : ${Array.isArray(errors.email) ? errors.email[0] : errors.email}`);
          } else if (errors.login) {
            this.errorMessage.set(`Identifiant : ${Array.isArray(errors.login) ? errors.login[0] : errors.login}`);
          } else if (errors.telephone) {
            const telephoneError = Array.isArray(errors.telephone) ? errors.telephone[0] : errors.telephone;
            const telephoneErrorText = String(telephoneError);
            this.errorMessage.set(
              telephoneErrorText.includes('UNIQUE constraint failed')
                ? 'Un utilisateur avec ce numéro de téléphone existe déjà.'
                : `Numéro de téléphone : ${telephoneError}`
            );
          } else if (errors.motDePasse) {
            this.errorMessage.set(`Mot de passe : ${Array.isArray(errors.motDePasse) ? errors.motDePasse[0] : errors.motDePasse}`);
          } else if (errors.message || errors.detail) {
            this.errorMessage.set(errors.message || errors.detail);
          } else {
            this.errorMessage.set('Certaines informations sont invalides ou déjà utilisées.');
          }
        } else if (err?.friendlyMessage) {
          this.errorMessage.set(err.friendlyMessage);
        } else {
          this.errorMessage.set('Une erreur est survenue lors de la création de votre compte. Veuillez vérifier vos données.');
        }
      }
    });
  }
}
