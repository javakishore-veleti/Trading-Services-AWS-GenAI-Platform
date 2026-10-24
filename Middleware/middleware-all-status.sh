#!/usr/bin/env bash
# Report every local middleware group. Add the next FastAPI group beside the MCP line.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/mcp-servers/mcp-all-status.sh"
