#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "FX API services"
"$DIR/api-services/api-all-status.sh"
echo
echo "FX question service"
"$DIR/agentic-ai-wfs/lang-graph/fx-desk-status.sh"
