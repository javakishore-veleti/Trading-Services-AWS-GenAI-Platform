#!/usr/bin/env bash
# Show the containers, then every middleware group.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"

"$DIR/docker-all-status.sh"
echo
echo "Middleware"
"$ROOT/Middleware/middleware-all-status.sh"
