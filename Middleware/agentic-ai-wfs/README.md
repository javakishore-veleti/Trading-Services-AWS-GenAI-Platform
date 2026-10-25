# Agentic workflows

`lang-graph` is the trading-desk runtime. Each desk is its own process. `aws-strands` and `agno` are the starter-kit example agents, also one process each. All three call LiteLLM for the model, and the seed registers every process so LiteLLM can call it back at `POST /runs/wait`. A prompt is what reaches the model.

The FX question in Ask TradesAI runs in `lang-graph/traders-agentic-wfs` on port 8601. The framework list also shows Strands and Agno. Those two are not connected yet. A turn with no framework uses LangGraph. That turn does not call a model. The quote, the history, and the recommendation come from the API services.
