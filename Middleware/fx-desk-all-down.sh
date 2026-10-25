#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/agentic-ai-wfs/lang-graph/fx-desk-down.sh"
"$DIR/api-services/api-all-down.sh"
