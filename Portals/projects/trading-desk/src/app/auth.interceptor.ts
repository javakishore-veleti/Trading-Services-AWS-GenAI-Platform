import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const raw = sessionStorage.getItem('trading-desk-session');
  if (!raw) {
    return next(request);
  }
  const session = JSON.parse(raw) as { token?: string };
  if (!session.token) {
    return next(request);
  }
  return next(request.clone({ setHeaders: { Authorization: `Bearer ${session.token}` } }));
};
