#!/usr/bin/env bash
# Stage 13 — Open WebUI chat interface wired to LiteLLM. Reach it with port-forward (no public ingress).
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/openwebui.yaml"

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    # The UI reads the LiteLLM key from its own namespace, so copy it there.
    ensure_secret litellm litellm-key LITELLM_MASTER_KEY
    kubectl -n litellm get secret litellm-key -o yaml | sed 's/namespace: litellm/namespace: openwebui/' \
      | kubectl apply -f -
    kubectl apply -f "$MANIFEST"
    kubectl -n openwebui rollout status deployment/open-webui --timeout=15m
    CODE=$(in_cluster_curl openwebui http://open-webui.openwebui.svc.cluster.local:8080/health -o /dev/null -w '%{http_code}' || true)
    summary "**Verified:** Open WebUI rollout complete (health returned ${CODE}). Open it with: kubectl -n openwebui port-forward svc/open-webui 8080:8080"
    ;;
  destroy)
    kubectl delete namespace openwebui --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** Open WebUI namespace."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
