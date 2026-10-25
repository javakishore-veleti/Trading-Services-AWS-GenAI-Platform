import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

interface Page {
  page: number;
  page_size: number;
  total: number;
  rows: Record<string, unknown>[];
}

export interface Field {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'checkbox' | 'list';
  options?: string[];
}

interface RecordData {
  title: string;
  list: string;
  create: string;
  fields: Field[];
}

@Component({
  selector: 'app-records',
  imports: [FormsModule],
  template: `
    <section class="sheet">
      <div class="sheet-head">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ total }} records</p>
        </div>
        <button type="button" (click)="toggle()">{{ adding ? 'Close' : 'Add' }}</button>
      </div>
      @if (adding) {
        <form class="add-form" (ngSubmit)="create()">
          @for (field of fields; track field.key) {
            <label [class.check]="field.type === 'checkbox'">
              @if (field.type === 'checkbox') {
                <input type="checkbox" [(ngModel)]="draft[field.key]" [name]="field.key" />
              }
              {{ field.label }}
              @if (field.options) {
                <select [(ngModel)]="draft[field.key]" [name]="field.key">
                  <option value="">Select</option>
                  @for (option of field.options; track option) {
                    <option [value]="option">{{ option }}</option>
                  }
                </select>
              } @else if (field.type !== 'checkbox') {
                <input
                  [(ngModel)]="draft[field.key]"
                  [name]="field.key"
                  [type]="field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'"
                />
              }
            </label>
          }
          <div class="actions">
            <button type="submit" [disabled]="busy">Save</button>
            <button type="button" class="flat" (click)="adding = false">Cancel</button>
          </div>
        </form>
      }
      <p class="error">{{ error }}</p>
      @if (!columns.length) {
        <p class="empty">Nothing is stored yet. Ingest the dataset, or add a record.</p>
      } @else {
        <table>
          <thead>
            <tr>
              @for (column of columns; track column) {
                <th>{{ heading(column) }}</th>
              }
            </tr>
          </thead>
          <tbody>
            @for (row of rows; track $index) {
              <tr>
                @for (column of columns; track column) {
                  <td>{{ cell(row, column) }}</td>
                }
              </tr>
            }
          </tbody>
        </table>
      }
      <div class="pager">
        <button type="button" class="flat" (click)="load(page - 1)" [disabled]="page <= 1">Previous</button>
        <span>Page {{ page }} of {{ pageCount }}</span>
        <button type="button" class="flat" (click)="load(page + 1)" [disabled]="page >= pageCount">Next</button>
      </div>
    </section>
  `,
})
export class RecordsComponent implements OnInit {
  title = '';
  fields: Field[] = [];
  rows: Record<string, unknown>[] = [];
  columns: string[] = [];
  page = 1;
  total = 0;
  pageSize = 20;
  error = '';
  busy = false;
  adding = false;
  draft: Record<string, string | boolean> = {};
  private listUrl = '';
  private createUrl = '';
  private readonly destroyRef = inject(DestroyRef);

  constructor(
    private readonly http: HttpClient,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.route.data.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((data) => {
      const page = data as RecordData;
      this.title = page.title;
      this.fields = page.fields;
      this.listUrl = page.list;
      this.createUrl = page.create;
      this.adding = false;
      this.error = '';
      this.reset();
      this.load(1);
    });
  }

  get pageCount(): number {
    return Math.max(1, Math.ceil(this.total / this.pageSize));
  }

  toggle(): void {
    this.adding = !this.adding;
    this.error = '';
    if (this.adding) {
      this.reset();
    }
  }

  create(): void {
    this.error = '';
    this.busy = true;
    this.http.post(this.createUrl, this.payload()).subscribe({
      next: () => {
        this.busy = false;
        this.adding = false;
        this.reset();
        this.load(1);
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.error = typeof error.error?.detail === 'string' ? error.error.detail : 'The record was not saved.';
      },
    });
  }

  load(page: number): void {
    this.http.get<Page>(this.listUrl, { params: { page, page_size: 20 } }).subscribe({
      next: (body) => {
        this.rows = body.rows;
        this.page = body.page;
        this.total = body.total;
        this.pageSize = body.page_size;
        this.columns = body.rows.length ? Object.keys(body.rows[0]) : this.columns;
      },
      error: (error: HttpErrorResponse) => {
        this.error = typeof error.error?.detail === 'string' ? error.error.detail : 'The list is unavailable.';
      },
    });
  }

  heading(column: string): string {
    return column.replaceAll('_', ' ');
  }

  cell(row: Record<string, unknown>, column: string): string {
    const value = row[column];
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    if (value !== null && typeof value === 'object') {
      return JSON.stringify(value);
    }
    return value == null ? '' : String(value);
  }

  private reset(): void {
    this.draft = {};
    for (const field of this.fields) {
      this.draft[field.key] = field.type === 'checkbox' ? false : '';
    }
  }

  private payload(): Record<string, unknown> {
    const body: Record<string, unknown> = {};
    for (const field of this.fields) {
      const value = this.draft[field.key];
      if (field.type === 'list') {
        body[field.key] = String(value)
          .split(',')
          .map((part) => part.trim())
          .filter((part) => part.length > 0);
      } else if (field.type === 'number') {
        body[field.key] = value === '' ? null : Number(value);
      } else if (field.type === 'checkbox') {
        body[field.key] = Boolean(value);
      } else {
        body[field.key] = value;
      }
    }
    return body;
  }
}
