#!/usr/bin/env bash
# Stop the LangGraph FX question service.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$DIR/traders-agentic-wfs/.run"

if [ -d "$RUN" ]; then
  for pidfile in "$RUN"/*.pid; do
    [ -e "$pidfile" ] || continue
    pid="$(cat "$pidfile")"
    kill "$pid" 2>/dev/null || true
    rm -f "$pidfile"
  done
fi

pids="$(lsof -ti tcp:8601 -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$pids" ]; then
  kill $pids 2>/dev/null || true
fi

echo "traders-agentic-wfs is down."
