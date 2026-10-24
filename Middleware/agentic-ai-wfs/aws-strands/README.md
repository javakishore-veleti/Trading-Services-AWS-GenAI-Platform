# Strands

Two processes from the starter-kit examples. Each one is its own uv project. Both call LiteLLM at `http://127.0.0.1:4000` with the model `deepseek-r1-8b-ollama`. A prompt is what reaches the model. Starting the process does not.

| Agent | Port | Call |
| --- | --- | --- |
| calculator-agent | 8301 | `POST /` with `{"prompt":"..."}` |
| loan-buddy-agent | 8302 | `POST /api/process_credit_application_with_upload` with an image file |

The calculator tools run in the process. The loan agent stores the upload under `.run/loan-images` and can only report that the file is there. Short-term messages and long-term facts sit in the platform Postgres schema `strands`. The kit's Kong route, Arize project, and workshop document MCP servers are not part of this stack.

Start both with `strands-all-up.sh`. The LiteLLM seed registers each one as `langgraph/strands-calculator-agent` and `langgraph/strands-loan-buddy-agent`. LiteLLM calls `POST /runs/wait` on `http://host.docker.internal:{port}`.
