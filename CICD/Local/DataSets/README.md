# Local FX datasets

These JSON files are the records the admin portal loads. Rates on historical orders are illustrative. Today's USD/INR quote is served by `trades-offers-services`, not by this history.

| Folder | File | Records |
|---|---|---|
| `Customers` | `customers.json` | 100 customers. `CUST-001` is Northwind Exports. `CUST-002` is Harbor Retail. |
| `TraderBooks` | `trader-books.json` | 20 books. `BOOK-01` is USD/INR. |
| `Traders` | `traders.json` | 100 traders. Each trader lists the customers that trader may work. |
| `Trader-Books-Mappings` | `trader-books-mappings.json` | 200 trader-to-book rows. `TRADER-001` sits on `BOOK-01`. |
| `Customer-Trades-History` | `orders.json` | Each order is an `order_header` plus `order_lines`. |

An order uses one of three products:

| Product | Meaning |
|---|---|
| Spot | Exchange at an agreed current rate. The settlement line is two business days after the order date. |
| Window Forward | The rate is agreed on the order date. Each line is a permitted date inside the window. |
| Currency Futures | A standardized contract with a fixed expiry and a margin line. |

The history covers USD, INR, GBP, JPY, and 25 further currencies. Northwind's four orders are the illustrative USD/INR history: two spot conversions and two window forwards, one with three partial dates and one spread across 20 days.

Regenerate with `python3 CICD/Local/DataSets/generate_datasets.py`.
