# Portals

Two Angular apps share this folder.

| App | Address | Sign-in |
|---|---|---|
| Trading Desk | http://127.0.0.1:4200 | `trader001` / `local-trader` |
| Admin | http://127.0.0.1:4201 | `admin` / `local-admin` |

Start the API services first with `npm run local::fx-desk::all:up`.

```bash
npm --prefix Portals install
npm run local::portal::admin
npm run local::portal::trading-desk
```

The admin menu bar has two items. Data Management shows when each synthetic dataset was last ingested, or Never, and the Ingest button. Desk Management lists each object with paging and an Add button: trading books, traders, book mappings, customers, and trade history. Ingest books and traders before mappings, and customers before trade history. Then sign in to the Trading Desk, choose Northwind Exports, leave the framework on LangGraph, and ask the USD 1 million question.

The dashboard route is a placeholder. Strands and Agno appear in the framework list and stay disabled until those runtimes are connected.
