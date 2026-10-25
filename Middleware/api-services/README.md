# API services

Each service is its own FastAPI process. Callers use the interface. A new behavior is a new implementation.

| Service | Port | Role |
|---|---|---|
| app-auth-service | 8501 | Admin and trader sign-in |
| traders-service | 8502 | Books, traders, trader-book mappings, and the customers a trader may work |
| customer-service | 8503 | Customers and FX order history |
| trades-catalog-service | 8504 | Spot, Window Forward, and Currency Futures |
| trades-offers-services | 8505 | Quotes. USD/INR indicative is 96 |
| trades-orders-service | 8506 | An order the trader confirms. The agents never call this |

Start them with `npm run local::api-services::all:up`.

Each synthetic dataset starts as `pending` in `trading_desk_admin.ingestion_status`. Ingest writes that file into its own schema: `trader_books`, `traders`, `trader_book_mappings`, `customers`, or `customer_trades`. Mappings need books and traders. History needs customers.

Local sign-in: admin `admin` / `local-admin`. Trader `trader001` / `local-trader`. The other traders use the same trader password. `trader001` is assigned to Northwind Exports and Harbor Retail.
