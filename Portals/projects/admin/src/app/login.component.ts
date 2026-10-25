import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  template: `
    <div class="login-wrap">
      <form class="login" (ngSubmit)="submit()">
        <div class="login-banner">
          <h1>Administration</h1>
        </div>
        <label for="username">Username</label>
        <input id="username" name="username" [(ngModel)]="username" autocomplete="username" />
        <label for="password">Password</label>
        <input id="password" name="password" type="password" [(ngModel)]="password" autocomplete="current-password" />
        <p class="error">{{ error }}</p>
        <button type="submit">Sign in</button>
      </form>
    </div>
  `,
})
export class LoginComponent {
  username = '';
  password = '';
  error = '';

  constructor(
    private readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  submit(): void {
    this.error = '';
    this.auth.login(this.username, this.password).subscribe({
      next: (session) => {
        if (session.role !== 'admin') {
          this.auth.logout();
          this.error = 'Use the administrator sign-in on this portal.';
          return;
        }
        void this.router.navigateByUrl('/data/books');
      },
      error: (error: HttpErrorResponse) => {
        this.error = typeof error.error?.detail === 'string' ? error.error.detail : 'Sign-in failed.';
      },
    });
  }
}
