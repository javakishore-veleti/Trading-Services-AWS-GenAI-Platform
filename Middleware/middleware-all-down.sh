#!/usr/bin/env bash
# Stop every local middleware group, in the reverse of middleware-all-up.sh.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/agentic-ai-wfs/lang-graph/lang-graph-all-down.sh"
"$DIR/mcp-servers/mcp-all-down.sh"
