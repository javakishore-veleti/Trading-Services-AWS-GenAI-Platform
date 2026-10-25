import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { Session } from './models';

const AUTH = 'http://127.0.0.1:8501';
const KEY = 'trading-desk-session';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly session = signal<Session | null>(this.read());

  constructor(private readonly http: HttpClient) {}

  login(username: string, password: string): Observable<Session & { token: string }> {
    return this.http.post<Session & { token: string }>(`${AUTH}/login`, { username, password }).pipe(
      tap((session) => {
        sessionStorage.setItem(KEY, JSON.stringify(session));
        this.session.set(session);
      }),
    );
  }

  logout(): void {
    sessionStorage.removeItem(KEY);
    this.session.set(null);
  }

  private read(): Session | null {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as Session;
  }
}
