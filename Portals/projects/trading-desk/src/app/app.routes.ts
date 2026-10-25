import { inject } from '@angular/core';
import { CanActivateFn, Router, Routes } from '@angular/router';
import { AskComponent } from './ask.component';
import { AuthService } from './auth.service';
import { DashboardComponent } from './dashboard.component';
import { LoginComponent } from './login.component';
import { ShellComponent } from './shell.component';

const traderGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.session()?.role === 'trader' ? true : router.createUrlTree(['/login']);
};

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [traderGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'ask' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'ask', component: AskComponent },
    ],
  },
];
