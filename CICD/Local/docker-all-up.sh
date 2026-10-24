#!/usr/bin/env bash
# Start the local stack, then seed LiteLLM. Each step lives in scripts/.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$DIR/scripts/start-datastores.sh"
"$DIR/scripts/start-llm-models.sh"
"$DIR/scripts/start-observability.sh"
"$DIR/scripts/start-tei.sh"
"$DIR/scripts/provision-pgvector.sh"
"$DIR/scripts/start-litellm.sh"
"$DIR/scripts/start-openwebui.sh"
"$DIR/scripts/start-n8n.sh"
"$DIR/scripts/seed-litellm.sh"
"$DIR/scripts/open-ui.sh"
