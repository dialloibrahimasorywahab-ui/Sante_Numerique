import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => next(req).pipe(
  catchError((error: HttpErrorResponse) => {
    console.error(`Erreur API ${error.status} sur ${req.url}`, error);
    return throwError(() => error);
  })
);
