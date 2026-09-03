import { HttpInterceptorFn } from '@angular/common/http';

/**
 * Intercepteur HTTP pour Santé Numérique :
 * Assure la transmission automatique des cookies HttpOnly (access_token et refresh_token)
 * pour toutes les requêtes adressées au backend Django.
 * Conforme à la directive de sécurité : aucun token JWT n'est lu ni manipulé côté JavaScript.
 */
export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const clonedReq = req.clone({
    withCredentials: true
  });

  return next(clonedReq);
};
