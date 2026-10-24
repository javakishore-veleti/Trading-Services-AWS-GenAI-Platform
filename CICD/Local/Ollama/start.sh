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
case "${OLLAMA_PULL:-true}" in
  0|false|FALSE|no|NO|off|OFF)
    echo "OLLAMA_PULL is false. ${OLLAMA_MODEL} was not pulled."
    ;;
  *)
    ollama pull "$OLLAMA_MODEL"
    ;;
esac
wait "$pid"
