import { inject } from '@angular/core';
import { CanActivateFn, Router, Routes } from '@angular/router';
import { AuthService } from './auth.service';
import { DatasetComponent } from './dataset.component';
import { LoginComponent } from './login.component';
import { Field, RecordsComponent } from './records.component';
import { ShellComponent } from './shell.component';

const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.session()?.role === 'admin' ? true : router.createUrlTree(['/login']);
};

const products = ['SPOT', 'WINDOW_FORWARD', 'CURRENCY_FUTURES'];

const bookFields: Field[] = [
  { key: 'book_id', label: 'Book id' },
  { key: 'name', label: 'Name' },
  { key: 'base_currency', label: 'Base currency' },
  { key: 'term_currency', label: 'Term currency' },
  { key: 'products', label: 'Products', type: 'list' },
];

const traderFields: Field[] = [
  { key: 'trader_id', label: 'Trader id' },
  { key: 'username', label: 'Username' },
  { key: 'display_name', label: 'Display name' },
  { key: 'desk', label: 'Desk' },
  { key: 'customer_ids', label: 'Customer ids', type: 'list' },
];

const mappingFields: Field[] = [
  { key: 'trader_id', label: 'Trader id' },
  { key: 'book_id', label: 'Book id' },
];

const customerFields: Field[] = [
  { key: 'customer_id', label: 'Customer id' },
  { key: 'name', label: 'Name' },
  { key: 'country', label: 'Country' },
  { key: 'resident', label: 'Resident', type: 'checkbox' },
  { key: 'preferred_product', label: 'Preferred product', options: products },
  { key: 'amount', label: 'Amount', type: 'number' },
  { key: 'currency', label: 'Currency' },
  { key: 'base_currency', label: 'Base currency' },
  { key: 'term_currency', label: 'Term currency' },
  { key: 'usd_available_now', label: 'USD available now', type: 'checkbox' },
  { key: 'dates', label: 'Settlement dates', type: 'list' },
];

const tradeFields: Field[] = [
  { key: 'order_id', label: 'Order id' },
  { key: 'customer_id', label: 'Customer id' },
  { key: 'book_id', label: 'Book id' },
  { key: 'product_id', label: 'Product', options: products },
  { key: 'base_currency', label: 'Base currency' },
  { key: 'term_currency', label: 'Term currency' },
  { key: 'amount', label: 'Amount', type: 'number' },
  { key: 'currency', label: 'Currency' },
  { key: 'order_date', label: 'Order date', type: 'date' },
  { key: 'value_date', label: 'Value date', type: 'date' },
  { key: 'rate', label: 'Rate', type: 'number' },
];

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [adminGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'data/books' },
      { path: 'books', pathMatch: 'full', redirectTo: 'data/books' },
      {
        path: 'data/books',
        component: DatasetComponent,
        data: {
          title: 'Trading Books',
          hint: 'TraderBooks/trader-books.json',
          statusUrl: 'http://127.0.0.1:8502/ingestion/trader_books',
          populate: 'http://127.0.0.1:8502/books/populate',
        },
      },
      {
        path: 'data/traders',
        component: DatasetComponent,
        data: {
          title: 'Traders',
          hint: 'Traders/traders.json',
          statusUrl: 'http://127.0.0.1:8502/ingestion/traders',
          populate: 'http://127.0.0.1:8502/traders/populate',
        },
      },
      {
        path: 'data/mappings',
        component: DatasetComponent,
        data: {
          title: 'Trader and Trading Book mappings',
          hint: 'Trader-Books-Mappings/trader-books-mappings.json',
          statusUrl: 'http://127.0.0.1:8502/ingestion/trader_book_mappings',
          populate: 'http://127.0.0.1:8502/trader-book-mappings/populate',
        },
      },
      {
        path: 'data/customers',
        component: DatasetComponent,
        data: {
          title: 'Customers',
          hint: 'Customers/customers.json',
          statusUrl: 'http://127.0.0.1:8503/ingestion/customers',
          populate: 'http://127.0.0.1:8503/customers/populate',
        },
      },
      {
        path: 'data/history',
        component: DatasetComponent,
        data: {
          title: 'Customer trades history',
          hint: 'Customer-Trades-History/orders.json',
          statusUrl: 'http://127.0.0.1:8503/ingestion/customer_trades_history',
          populate: 'http://127.0.0.1:8503/customer-trades-history/populate',
        },
      },
      {
        path: 'desk/books',
        component: RecordsComponent,
        data: {
          title: 'Trading Books',
          list: 'http://127.0.0.1:8502/books',
          create: 'http://127.0.0.1:8502/books',
          fields: bookFields,
        },
      },
      {
        path: 'desk/traders',
        component: RecordsComponent,
        data: {
          title: 'Traders',
          list: 'http://127.0.0.1:8502/traders',
          create: 'http://127.0.0.1:8502/traders',
          fields: traderFields,
        },
      },
      {
        path: 'desk/mappings',
        component: RecordsComponent,
        data: {
          title: 'Trader and Trading Book mappings',
          list: 'http://127.0.0.1:8502/trader-book-mappings',
          create: 'http://127.0.0.1:8502/trader-book-mappings',
          fields: mappingFields,
        },
      },
      {
        path: 'desk/customers',
        component: RecordsComponent,
        data: {
          title: 'Customers',
          list: 'http://127.0.0.1:8503/customers',
          create: 'http://127.0.0.1:8503/customers',
          fields: customerFields,
        },
      },
      {
        path: 'desk/history',
        component: RecordsComponent,
        data: {
          title: 'Customer trades history',
          list: 'http://127.0.0.1:8503/customer-trades-history',
          create: 'http://127.0.0.1:8503/orders',
          fields: tradeFields,
        },
      },
    ],
  },
];
