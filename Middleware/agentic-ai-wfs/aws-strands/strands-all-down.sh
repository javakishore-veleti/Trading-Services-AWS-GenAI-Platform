#!/usr/bin/env bash
# Stop the Strands processes started by strands-all-up.sh.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$DIR/.run"

stop_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti "tcp:${port}" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$pids" ]; then
    kill $pids 2>/dev/null || true
  fi
}

if [ -d "$RUN" ]; then
  for pidfile in "$RUN"/*.pid; do
    [ -e "$pidfile" ] || continue
    pid="$(cat "$pidfile")"
    kill "$pid" 2>/dev/null || true
    rm -f "$pidfile"
  done
fi

for port in 8301 8302; do
  stop_port "$port"
done

echo "Strands agents are down."
