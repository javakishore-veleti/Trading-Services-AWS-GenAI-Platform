#!/usr/bin/env bash
# Stop the desk agent processes started by lang-graph-all-up.sh.
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

for port in 8201 8202 8203 8204 8205; do
  stop_port "$port"
done

echo "Desk agents are down."
