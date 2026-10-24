#!/usr/bin/env bash
# Report every local middleware group. Add the next FastAPI group beside the MCP line.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "MCP servers"
"$DIR/mcp-servers/mcp-all-status.sh"
echo
echo "Desk agents"
"$DIR/agentic-ai-wfs/lang-graph/lang-graph-all-status.sh"
echo
echo "Strands agents"
"$DIR/agentic-ai-wfs/aws-strands/strands-all-status.sh"
echo
echo "Agno"
"$DIR/agentic-ai-wfs/agno/agno-all-status.sh"
