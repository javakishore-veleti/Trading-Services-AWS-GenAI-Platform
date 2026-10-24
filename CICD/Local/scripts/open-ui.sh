#!/usr/bin/env bash
# Print the local gateway address and open the Admin UI on macOS.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

echo "LiteLLM is up."
echo "Username: ${UI_ADMIN_EMAIL:-admin@localhost}"
echo "Password: ${UI_ADMIN_PASSWORD:-}"
echo "Admin UI:"
echo "${LITELLM_UI}"
echo "API docs:"
echo "${LITELLM_DOCS}"
if [ "$(uname -s)" = "Darwin" ]; then
  open "${LITELLM_UI}"
fi
