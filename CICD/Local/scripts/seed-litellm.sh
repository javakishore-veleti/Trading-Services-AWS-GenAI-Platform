#!/usr/bin/env bash
# Register teams, budgets, vector stores, indexes, MCP servers, toolsets, skills, guardrails, desk agents, and app users on the running proxy.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

echo "Ensuring the Admin UI account..."
python3 "$SCRIPTS_DIR/seed-litellm.py" "$ROOT/.env"
