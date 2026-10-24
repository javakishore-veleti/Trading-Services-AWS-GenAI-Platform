#!/usr/bin/env bash
# Stage 09 — smoke test: nginx behind an Auto Mode ALB. Proves network, cluster, load balancer and pods work.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/smoke.yaml"

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    kubectl apply -f "$MANIFEST"
    kubectl -n smoke rollout status deployment/smoke --timeout=5m
    HOST=""
    for _ in $(seq 1 40); do
      HOST=$(kubectl -n smoke get ingress smoke -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
      [ -n "$HOST" ] && break
      sleep 15
    done
    [ -n "$HOST" ] || { echo "FAIL: ALB hostname not assigned after 10 minutes"; exit 1; }
    summary "ALB: \`http://${HOST}/\`"
    for _ in $(seq 1 20); do
      CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://${HOST}/" || true)
      [ "$CODE" = 200 ] && break
      sleep 15
    done
    [ "$CODE" = 200 ] || { echo "FAIL: ALB returned ${CODE}"; exit 1; }
    summary "**Verified:** http://${HOST}/ returned 200."
    ;;
  destroy)
    kubectl delete -f "$MANIFEST" --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** smoke app and its ALB."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
