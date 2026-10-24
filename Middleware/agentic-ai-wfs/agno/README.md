# Agno

One process from the starter-kit calculator example. It is its own uv project. It calls LiteLLM at `http://127.0.0.1:4000` with the model `deepseek-r1-8b-ollama`. A prompt is what reaches the model. Starting the process does not.

| Agent | Port | Call |
| --- | --- | --- |
| calculator-agent | 8401 | `POST /` with `{"prompt":"..."}` |

The calculator tools run in the process. Session rows sit in `.run/calculator.db`. The kit's calculator MCP server is not part of this stack.

Start it with `agno-all-up.sh`. The LiteLLM seed registers it as `langgraph/agno-calculator-agent`. LiteLLM calls `POST /runs/wait` on `http://host.docker.internal:8401`.
