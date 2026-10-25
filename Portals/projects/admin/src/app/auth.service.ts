import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

export interface Session {
  token: string;
  role: string;
  trader_id: string;
  display_name: string;
  username: string;
}

const KEY = 'admin-session';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly session = signal<Session | null>(this.read());

  constructor(private readonly http: HttpClient) {}

  login(username: string, password: string): Observable<Session> {
    return this.http.post<Session>('http://127.0.0.1:8501/login', { username, password }).pipe(
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
    return raw ? (JSON.parse(raw) as Session) : null;
  }
}
