#!/usr/bin/env bash
# Containers first. docker-all-up returns only after they are healthy, then middleware starts.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"

"$DIR/docker-all-up.sh"
"$ROOT/Middleware/middleware-all-up.sh"
