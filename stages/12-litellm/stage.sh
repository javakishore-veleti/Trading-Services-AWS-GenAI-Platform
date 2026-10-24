#!/usr/bin/env bash
# Stage 12 — LiteLLM gateway in front of vLLM. Master key is generated into a cluster secret, never printed.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/litellm.yaml"

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    kubectl apply -f "$MANIFEST"
    ensure_secret litellm litellm-key LITELLM_MASTER_KEY
    kubectl -n litellm rollout restart deployment/litellm >/dev/null
    kubectl -n litellm rollout status deployment/litellm --timeout=10m
    CODE=$(in_cluster_curl litellm http://litellm.litellm.svc.cluster.local:4000/health/liveliness -o /dev/null -w '%{http_code}' || true)
    echo "liveliness HTTP ${CODE}"
    summary "**Verified:** LiteLLM rollout complete (liveliness returned ${CODE}). Master key is in secret litellm-key."
    ;;
  destroy)
    kubectl delete namespace litellm --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** LiteLLM namespace."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
