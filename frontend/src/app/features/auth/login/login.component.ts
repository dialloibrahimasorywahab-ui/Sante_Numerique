import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  loginForm!: FormGroup;
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  showPassword = signal<boolean>(false);
  showForgotPasswordModal = signal<boolean>(false);

  private returnUrl: string = '';

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';

    // Si un message de succès d'inscription est transmis
    if (this.route.snapshot.queryParams['registered']) {
      this.successMessage.set('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.');
    }

    this.initForm();

    // Empêcher tout pré-remplissage résiduel ou automatique du navigateur
    setTimeout(() => {
      this.loginForm.reset({ login: '', motDePasse: '' });
    }, 50);
  }

  private initForm(): void {
    this.loginForm = this.fb.group({
      login: ['', [Validators.required]],
      motDePasse: ['', [Validators.required]]
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(prev => !prev);
  }

  openForgotPassword(event: Event): void {
    event.preventDefault();
    this.showForgotPasswordModal.set(true);
  }

  closeForgotPassword(): void {
    this.showForgotPasswordModal.set(false);
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const { login, motDePasse } = this.loginForm.value;

    this.authService.login({
      login: login.trim(),
      motDePasse
    }).subscribe({
      next: (user) => {
        this.isLoading.set(false);

        if (this.returnUrl && !this.returnUrl.includes('/login') && !this.returnUrl.includes('/register')) {
          this.router.navigateByUrl(this.returnUrl);
        } else {
          const targetRoute = this.authService.getDashboardRouteForRole(user.role);
          this.router.navigate([targetRoute]);
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err?.friendlyMessage) {
          this.errorMessage.set(err.friendlyMessage);
        } else if (err?.status === 401) {
          this.errorMessage.set('Identifiants incorrects.');
        } else if (err?.status === 403) {
          this.errorMessage.set('Compte désactivé. Veuillez contacter l’administrateur.');
        } else if (err?.status === 400) {
          this.errorMessage.set('L’identifiant et le mot de passe sont requis.');
        } else {
          this.errorMessage.set('Une erreur est survenue. Veuillez réessayer.');
        }
      }
    });
  }
}
