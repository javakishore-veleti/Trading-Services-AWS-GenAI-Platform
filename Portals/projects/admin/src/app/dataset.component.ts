import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';

interface IngestionStatus {
  dataset_key: string;
  title: string;
  schema_name: string;
  status: string;
  record_count: number;
  message: string;
  ingested_at: string | null;
}

interface DatasetData {
  title: string;
  hint: string;
  statusUrl: string;
  populate: string;
}

@Component({
  selector: 'app-dataset',
  template: `
    <div class="stats">
      <article class="stat">
        <div>
          <span>Last ingested</span>
          <strong>{{ lastIngested }}</strong>
          <em>{{ ingestion?.schema_name || 'Waiting for status' }}</em>
        </div>
        <div class="tile cyan"><span class="material-icons">schedule</span></div>
      </article>
      <article class="stat">
        <div>
          <span>Status</span>
          <strong>{{ ingestion?.status || 'pending' }}</strong>
          <em>{{ statusLine }}</em>
        </div>
        <div class="tile {{ statusTile }}"><span class="material-icons">{{ statusIcon }}</span></div>
      </article>
      <article class="stat">
        <div>
          <span>Records written</span>
          <strong>{{ recordCount }}</strong>
          <em>{{ hint }}</em>
        </div>
        <div class="tile green"><span class="material-icons">inventory_2</span></div>
      </article>
    </div>
    <section class="sheet">
      <div class="sheet-head">
        <div>
          <h1>{{ title }}</h1>
          <p>Ingest loads the synthetic file into its schema. Records are managed under Desk Management.</p>
        </div>
        <button type="button" (click)="ingest()" [disabled]="busy || ingestion?.status === 'ingesting'">
          {{ busy || ingestion?.status === 'ingesting' ? 'Ingesting…' : 'Ingest' }}
        </button>
      </div>
      <p class="error">{{ error }}</p>
    </section>
  `,
})
export class DatasetComponent implements OnInit {
  title = '';
  hint = '';
  error = '';
  busy = false;
  ingestion: IngestionStatus | null = null;
  private statusUrl = '';
  private populateUrl = '';
  private readonly destroyRef = inject(DestroyRef);

  constructor(
    private readonly http: HttpClient,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.route.data.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((data) => {
      const page = data as DatasetData;
      this.title = page.title;
      this.hint = page.hint;
      this.statusUrl = page.statusUrl;
      this.populateUrl = page.populate;
      this.error = '';
      this.refresh();
    });
  }

  get lastIngested(): string {
    const raw = this.ingestion?.ingested_at;
    if (!raw) {
      return 'Never';
    }
    return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(raw));
  }

  get recordCount(): string {
    if (this.ingestion?.status !== 'ingested') {
      return '—';
    }
    return String(this.ingestion.record_count);
  }

  get statusLine(): string {
    const state = this.ingestion?.status ?? 'pending';
    if (state === 'pending') {
      return 'Not ingested yet.';
    }
    if (state === 'ingesting') {
      return 'Ingest is in progress.';
    }
    if (state === 'failed') {
      return this.ingestion?.message || 'The last ingest failed.';
    }
    return 'The last ingest succeeded.';
  }

  get statusTile(): string {
    const state = this.ingestion?.status ?? 'pending';
    if (state === 'ingested') {
      return 'green';
    }
    if (state === 'failed') {
      return 'red';
    }
    if (state === 'ingesting') {
      return 'purple';
    }
    return 'orange';
  }

  get statusIcon(): string {
    const state = this.ingestion?.status ?? 'pending';
    if (state === 'ingested') {
      return 'check_circle';
    }
    if (state === 'failed') {
      return 'error';
    }
    if (state === 'ingesting') {
      return 'sync';
    }
    return 'hourglass_empty';
  }

  ingest(): void {
    this.error = '';
    this.busy = true;
    this.http.post(this.populateUrl, {}).subscribe({
      next: () => {
        this.busy = false;
        this.refresh();
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.error = typeof error.error?.detail === 'string' ? error.error.detail : 'Ingest failed.';
        this.refresh();
      },
    });
  }

  private refresh(): void {
    this.http.get<IngestionStatus>(this.statusUrl).subscribe({
      next: (status) => {
        this.ingestion = status;
      },
      error: (error: HttpErrorResponse) => {
        this.ingestion = null;
        this.error = typeof error.error?.detail === 'string' ? error.error.detail : 'Ingestion status is unavailable.';
      },
    });
  }
}
