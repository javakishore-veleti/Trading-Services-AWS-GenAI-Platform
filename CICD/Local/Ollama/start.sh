#!/bin/bash
set -eu
ollama serve &
pid=$!
i=0
while [ "$i" -lt 30 ]; do
  if ollama list >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done
ollama pull "$OLLAMA_MODEL"
wait "$pid"
