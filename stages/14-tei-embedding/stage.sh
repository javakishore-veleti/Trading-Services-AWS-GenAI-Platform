#!/usr/bin/env bash
# Stage 14 — CPU embedding service (TEI, Qwen3-Embedding-0.6B). Used later by the vector database.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/tei.yaml"

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    kubectl apply -f "$MANIFEST"
    kubectl -n tei rollout status deployment/tei-qwen3-embedding --timeout=20m
    OUT=$(kubectl run "verify-$RANDOM" -n tei --rm -i --restart=Never --quiet --image=curlimages/curl:8.10.1 -- \
      curl -sS --max-time 60 -X POST -H 'Content-Type: application/json' \
      -d '{"inputs":"hello world"}' http://tei-qwen3-embedding.tei.svc.cluster.local/embed || true)
    echo "$OUT" | head -c 200; echo
    echo "$OUT" | grep -q '\[\[' || { echo "FAIL: /embed did not return a vector"; exit 1; }
    summary "**Verified:** /embed returned a vector."
    ;;
  destroy)
    kubectl delete namespace tei --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** TEI namespace."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
