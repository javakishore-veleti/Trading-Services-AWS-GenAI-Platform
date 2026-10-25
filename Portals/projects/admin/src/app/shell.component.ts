import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './auth.service';

interface SideLink {
  path: string;
  label: string;
  icon: string;
}

interface Section {
  label: string;
  path: string;
  links: SideLink[];
}

const OBJECTS: SideLink[] = [
  { path: 'books', label: 'Trading Books', icon: 'menu_book' },
  { path: 'traders', label: 'Traders', icon: 'badge' },
  { path: 'mappings', label: 'Book mappings', icon: 'account_tree' },
  { path: 'customers', label: 'Customers', icon: 'groups' },
  { path: 'history', label: 'Trade history', icon: 'receipt_long' },
];

@Component({
  selector: 'app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="desk">
      <aside class="rail">
        <div class="brand"><span class="material-icons">account_balance</span> Administration</div>
        <div class="person">
          <div class="avatar">{{ initials }}</div>
          <div>
            <strong>{{ name }}</strong>
            <small>Administrator</small>
          </div>
        </div>
        <nav class="rail-nav">
          @for (link of active.links; track link.path) {
            <a [routerLink]="link.path" routerLinkActive="active">
              <span class="material-icons">{{ link.icon }}</span>
              {{ link.label }}
            </a>
          }
        </nav>
      </aside>
      <section class="stage">
        <header class="menu">
          <nav>
            @for (section of sections; track section.path) {
              <a [routerLink]="section.path" [class.active]="active === section">{{ section.label }}</a>
            }
          </nav>
          <div class="menu-end">
            <button type="button" class="flat" (click)="logout()">Sign out</button>
          </div>
        </header>
        <main>
          <router-outlet />
        </main>
      </section>
    </div>
  `,
})
export class ShellComponent {
  readonly sections: Section[] = [
    { label: 'Data Management', path: '/data/books', links: OBJECTS.map((item) => ({ ...item, path: `/data/${item.path}` })) },
    { label: 'Desk Management', path: '/desk/books', links: OBJECTS.map((item) => ({ ...item, path: `/desk/${item.path}` })) },
  ];

  constructor(
    readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  get name(): string {
    return this.auth.session()?.display_name || 'Admin';
  }

  get initials(): string {
    return this.name
      .split(' ')
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('');
  }

  get active(): Section {
    const url = this.router.url;
    return this.sections.find((section) => url.startsWith(section.path.startsWith('/data') ? '/data' : '/desk')) ?? this.sections[0];
  }

  logout(): void {
    this.auth.logout();
    void this.router.navigateByUrl('/login');
  }
}
