# Agentic workflows

`lang-graph` is the trading-desk runtime. Each desk is its own process. `aws-strands` and `agno` are the starter-kit example agents, also one process each. All three call LiteLLM for the model, and the seed registers every process so LiteLLM can call it back at `POST /runs/wait`. A prompt is what reaches the model.
