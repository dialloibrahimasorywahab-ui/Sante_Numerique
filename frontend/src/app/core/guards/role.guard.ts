import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/user.model';

/**
 * Garde de route vérifiant si l'utilisateur connecté possède l'un des rôles requis
 * (PATIENT, MEDECIN, INFIRMIER, ADMINISTRATEUR).
 */
export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    return router.createUrlTree(['/login'], {
      queryParams: { returnUrl: state.url }
    });
  }

  const allowedRoles = route.data['roles'] as UserRole[] | undefined;
  const currentRole = authService.currentUser()?.role;

  if (allowedRoles && currentRole && allowedRoles.includes(currentRole)) {
    return true;
  }

  // Redirection vers l'espace propre au rôle si non autorisé sur cette vue
  const targetRoute = authService.getDashboardRouteForRole(currentRole);
  return router.createUrlTree([targetRoute]);
};
