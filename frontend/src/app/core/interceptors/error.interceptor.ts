import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

/**
 * Intercepteur d'erreurs HTTP :
 * Assure un formatage sécurisé et convivial des messages d'erreurs (400, 401, 403, 404, 409, 500)
 * sans jamais exposer de stack trace Django ni de données sensibles.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let friendlyMessage = 'Une erreur est survenue. Veuillez réessayer.';

      if (error.status === 400) {
        if (typeof error.error === 'object' && error.error !== null) {
          const firstKey = Object.keys(error.error)[0];
          const firstVal = error.error[firstKey];
          if (Array.isArray(firstVal) && firstVal.length > 0) {
            friendlyMessage = firstVal[0];
          } else if (typeof firstVal === 'string') {
            friendlyMessage = firstVal;
          } else {
            friendlyMessage = error.error.message || error.error.detail || 'Les données fournies sont incomplètes ou invalides.';
          }
        } else {
          friendlyMessage = 'Les données fournies sont invalides.';
        }
      } else if (error.status === 401) {
        if (req.url.includes('/users/login/')) {
          friendlyMessage = 'Identifiants incorrects.';
        } else {
          friendlyMessage = 'Votre session a expiré. Veuillez vous reconnecter.';
        }
      } else if (error.status === 403) {
        friendlyMessage = error.error?.message || 'Vous n’avez pas les autorisations nécessaires.';
      } else if (error.status === 404) {
        friendlyMessage = 'La ressource demandée est introuvable.';
      } else if (error.status === 409) {
        friendlyMessage = 'Un conflit est survenu avec les informations fournies.';
      } else if (error.status >= 500) {
        friendlyMessage = 'Une erreur est survenue sur le serveur. Veuillez réessayer.';
      }

      const enhanced = Object.assign(error, { friendlyMessage });
      return throwError(() => enhanced);
    })
  );
};
