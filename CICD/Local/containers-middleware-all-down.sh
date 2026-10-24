#!/usr/bin/env bash
# Stop middleware first, then the containers.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"

"$ROOT/Middleware/middleware-all-down.sh"
"$DIR/docker-all-down.sh"
