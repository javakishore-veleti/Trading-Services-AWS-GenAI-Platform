import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './auth.service';

interface TopLink {
  path: string;
  label: string;
}

interface Section {
  label: string;
  path: string;
  links: TopLink[];
}

@Component({
  selector: 'app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="app">
      <header class="topbar">
        <div class="brand"><span class="mark"></span> Trading Desk</div>
        <nav class="top-links">
          @for (link of active.links; track link.path) {
            <a [routerLink]="link.path" routerLinkActive="active">{{ link.label }}</a>
          }
        </nav>
        <div class="session">
          <span>{{ auth.session()?.display_name }}</span>
          <button type="button" class="quiet" (click)="logout()">Sign out</button>
        </div>
      </header>
      <div class="workspace">
        <aside class="side">
          @for (section of sections; track section.path) {
            <a [routerLink]="section.path" [class.active]="active === section">{{ section.label }}</a>
          }
        </aside>
        <main>
          <router-outlet />
        </main>
      </div>
    </div>
  `,
})
export class ShellComponent {
  readonly sections: Section[] = [
    { label: 'Dashboard', path: '/dashboard', links: [{ path: '/dashboard', label: 'Overview' }] },
    { label: 'Ask TradesAI', path: '/ask', links: [{ path: '/ask', label: 'Conversation' }] },
  ];

  constructor(
    readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  get active(): Section {
    const url = this.router.url;
    return this.sections.find((section) => url.startsWith(section.path)) ?? this.sections[0];
  }

  logout(): void {
    this.auth.logout();
    void this.router.navigateByUrl('/login');
  }
}
