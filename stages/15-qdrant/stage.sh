#!/usr/bin/env bash
# Stage 15 — Qdrant vector database on an EBS volume (Auto Mode storage class auto-ebs-sc).
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/qdrant.yaml"

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    kubectl apply -f "$MANIFEST"
    kubectl -n qdrant rollout status statefulset/qdrant --timeout=15m
    CODE=$(in_cluster_curl qdrant http://qdrant.qdrant.svc.cluster.local:6333/readyz -o /dev/null -w '%{http_code}' || true)
    summary "**Verified:** Qdrant ready (readyz returned ${CODE})."
    ;;
  destroy)
    kubectl delete namespace qdrant --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** Qdrant namespace and its EBS volumes (volumes are deleted with the PVCs)."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
