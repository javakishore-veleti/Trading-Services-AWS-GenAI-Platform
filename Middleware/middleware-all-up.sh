#!/usr/bin/env bash
# Start every local middleware group. Containers are already healthy.
# Add the next FastAPI group as another line, after the groups it calls.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/mcp-servers/mcp-all-up.sh"
"$DIR/agentic-ai-wfs/lang-graph/lang-graph-all-up.sh"
