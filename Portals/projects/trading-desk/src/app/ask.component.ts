import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from './auth.service';
import { CustomerOption, FrameworkChoice, Turn, TurnPage } from './models';

const TRADERS = 'http://127.0.0.1:8502';
const CUSTOMERS = 'http://127.0.0.1:8503';
const DESK = 'http://127.0.0.1:8601';
const ORDERS = 'http://127.0.0.1:8506';

@Component({
  selector: 'app-ask',
  imports: [FormsModule],
  template: `
    <section>
      <div class="top">
        <h1>Ask TradesAI</h1>
        <label>
          Customer
          <select [(ngModel)]="customerId" (ngModelChange)="load(1)">
            <option value="">Select a customer</option>
            @for (customer of customers; track customer.customer_id) {
              <option [value]="customer.customer_id">{{ customer.name }}</option>
            }
          </select>
        </label>
      </div>
      <p class="error">{{ error }}</p>
      @for (turn of turns; track turn.turn_id) {
        <article class="card">
          <p><strong>{{ turn.question }}</strong></p>
          <p>{{ turn.framework }} · {{ turn.connected ? 'connected' : 'not connected' }}</p>
          @if (turn.message) {
            <p>{{ turn.message }}</p>
          }
          @for (agent of turn.agents; track agent.agent) {
            <p><strong>{{ agent.agent }}</strong> · {{ agent.model }}</p>
            <p>{{ agent.summary }}</p>
          }
          @if (turn.recommendation) {
            <p class="product">{{ turn.recommendation.product_name }}</p>
            <p>{{ turn.recommendation.rationale }}</p>
            <p><strong>Why not the others</strong></p>
            @for (item of turn.recommendation.alternatives; track item.product_name) {
              <p>{{ item.product_name }}: {{ item.reason }}</p>
            }
            <p><strong>Risks</strong></p>
            @for (risk of turn.recommendation.risks; track risk) {
              <p>{{ risk }}</p>
            }
            @if (turn.confirm_allowed) {
              <button type="button" (click)="confirm(turn)">Trader confirms</button>
            }
          }
          @if (confirmed[turn.turn_id]) {
            <p>{{ confirmed[turn.turn_id] }}</p>
          }
        </article>
      }
      <div class="pager">
        <button type="button" (click)="load(page - 1)" [disabled]="page <= 1">Newer</button>
        <span>Page {{ page }} of {{ pageCount }}</span>
        <button type="button" (click)="load(page + 1)" [disabled]="page >= pageCount">Older</button>
      </div>
      <form class="composer" (ngSubmit)="ask()">
        <label>
          Framework
          <select [(ngModel)]="framework" name="framework">
            @for (item of frameworks; track item.id) {
              <option [value]="item.id" [disabled]="!item.connected">
                {{ item.label }}{{ item.connected ? '' : ' (not connected)' }}
              </option>
            }
          </select>
        </label>
        <textarea name="message" rows="4" [(ngModel)]="message" placeholder="Ask about Spot, Window Forward, or Currency Futures"></textarea>
        <button type="submit" [disabled]="busy || !customerId || !message.trim()">Ask</button>
      </form>
    </section>
  `,
})
export class AskComponent implements OnInit {
  customers: CustomerOption[] = [];
  frameworks: FrameworkChoice[] = [{ id: 'langgraph', label: 'LangGraph', connected: true }];
  customerId = '';
  framework = 'langgraph';
  message = '';
  turns: Turn[] = [];
  page = 1;
  total = 0;
  pageSize = 5;
  error = '';
  busy = false;
  confirmed: Record<string, string> = {};

  constructor(
    private readonly http: HttpClient,
    private readonly auth: AuthService,
  ) {}

  ngOnInit(): void {
    const traderId = this.auth.session()?.trader_id ?? '';
    this.http.get<{ frameworks: FrameworkChoice[]; default: string }>(`${DESK}/frameworks`).subscribe({
      next: (body) => {
        this.frameworks = body.frameworks;
        this.framework = body.default || 'langgraph';
      },
    });
    this.http.get<{ customer_ids: string[] }>(`${TRADERS}/traders/${traderId}/customers`).subscribe({
      next: (body) => {
        this.http.post<{ customers: CustomerOption[] }>(`${CUSTOMERS}/customers/lookup`, {
          customer_ids: body.customer_ids,
        }).subscribe({
          next: (found) => {
            this.customers = found.customers;
            if (this.customers.length === 0) {
              this.error = 'No customers are loaded. Open the admin portal and populate customers.';
            }
          },
          error: () => {
            this.error = 'Customer service is not ready.';
          },
        });
      },
      error: () => {
        this.error = 'Populate traders in the admin portal before choosing a customer.';
      },
    });
  }

  get pageCount(): number {
    return Math.max(1, Math.ceil(this.total / this.pageSize));
  }

  load(page: number): void {
    if (!this.customerId) {
      this.turns = [];
      this.total = 0;
      this.page = 1;
      return;
    }
    this.http.get<TurnPage>(`${DESK}/turns`, { params: { customer_id: this.customerId, page, page_size: 5 } }).subscribe({
      next: (body) => this.apply(body),
      error: (error: HttpErrorResponse) => {
        this.error = this.detail(error);
      },
    });
  }

  ask(): void {
    this.error = '';
    this.busy = true;
    this.http.post<TurnPage>(`${DESK}/turns`, {
      customer_id: this.customerId,
      message: this.message,
      framework: this.framework || 'langgraph',
    }).subscribe({
      next: (body) => {
        this.message = '';
        this.busy = false;
        this.apply(body);
      },
      error: (error: HttpErrorResponse) => {
        this.busy = false;
        this.error = this.detail(error);
      },
    });
  }

  confirm(turn: Turn): void {
    if (!turn.recommendation) {
      return;
    }
    this.http.post<{ order_id: string }>(`${ORDERS}/orders`, {
      customer_id: turn.customer_id,
      product_id: turn.recommendation.product_id,
      amount: turn.recommendation.amount,
      currency: turn.recommendation.currency,
      turn_id: turn.turn_id,
    }).subscribe({
      next: (order) => {
        this.confirmed[turn.turn_id] = `Trader confirmed. ${order.order_id} is recorded. The agent did not book it.`;
      },
      error: (error: HttpErrorResponse) => {
        this.error = this.detail(error);
      },
    });
  }

  private apply(body: TurnPage): void {
    this.turns = body.turns;
    this.page = body.page;
    this.total = body.total;
    this.pageSize = body.page_size;
  }

  private detail(error: HttpErrorResponse): string {
    return typeof error.error?.detail === 'string' ? error.error.detail : 'The desk could not answer.';
  }
}
