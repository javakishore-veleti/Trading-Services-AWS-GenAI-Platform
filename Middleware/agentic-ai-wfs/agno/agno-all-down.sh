#!/usr/bin/env bash
# Stop the Agno process started by agno-all-up.sh.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$DIR/.run"

if [ -d "$RUN" ]; then
  for pidfile in "$RUN"/*.pid; do
    [ -e "$pidfile" ] || continue
    pid="$(cat "$pidfile")"
    kill "$pid" 2>/dev/null || true
    rm -f "$pidfile"
  done
fi

pids="$(lsof -ti tcp:8401 -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$pids" ]; then
  kill $pids 2>/dev/null || true
fi

echo "Agno calculator is down."
