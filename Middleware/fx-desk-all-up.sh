#!/usr/bin/env bash
# API services, then the LangGraph FX question service. Does not start the other desks.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/api-services/api-all-up.sh"
"$DIR/agentic-ai-wfs/lang-graph/fx-desk-up.sh"
