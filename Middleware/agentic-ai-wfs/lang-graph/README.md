# LangGraph

This folder is the runtime. Each FOREX trading desk is its own process and its own uv project. The workflow inside that process is the parent. It calls that desk's sub-agents and keeps the business process moving.

| Agent | Port | Process | Sub-agents |
| --- | --- | --- | --- |
| trading-desk-offers | 8201 | Rating, discount, then the all-in quote | offer-book |
| trading-desk-bffs | 8202 | Carry the screen request to the offer book and the order book | catalog, offer-book, order-book |
| trading-desk-io | 8203 | Catalog, then offer, then order for the eight countries | catalog, offer-book, order-book |
| trading-desk-order | 8204 | New, cancel, upgrade, or downgrade | order-book |
| trading-desk-platforms | 8205 | Carry Salesforce or Shopify to the offer book and the order book | catalog, offer-book, order-book |

Each sub-agent has its own Redis key and does not read the others. The parent stores a one-line summary of older results and a preview of the latest one. The full tool result stays in Redis. Retrieve reads that record back. Each agent loads only its own skill file.

A screen preview drops the discount and the timing. A platform preview also drops the all-in, and the platform agent does not place an order.

Start all five with `lang-graph-all-up.sh`. Invoke is `POST /agents/{agent}/invoke` on that agent's port. The LiteLLM seed registers each one as a LangGraph agent. The model is `langgraph/{agent}` and the API base is `http://host.docker.internal:{port}`. LiteLLM calls `POST /runs/wait` on that base. A message is JSON with `context_id`, `tool`, and `arguments`.
