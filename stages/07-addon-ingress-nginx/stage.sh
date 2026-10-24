#!/usr/bin/env bash
# Stage 07 — ingress-nginx behind a network load balancer, with optional HTTP basic auth.
# Basic auth is enabled only when BASIC_AUTH_USER and BASIC_AUTH_PASSWORD are set in GitHub Secrets.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require CLUSTER_NAME
NS=ingress-nginx

case "$ACTION" in
  plan)
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx >/dev/null 2>&1 || true
    helm repo update >/dev/null
    helm template ingress-nginx ingress-nginx/ingress-nginx -n "$NS" \
      --set controller.service.type=LoadBalancer --set controller.service.loadBalancerClass=eks.amazonaws.com/nlb \
      --set controller.ingressClassResource.default=false >/dev/null
    summary "Helm chart renders; would install ingress-nginx in namespace ${NS}."
    ;;
  apply)
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx >/dev/null 2>&1 || true
    helm repo update >/dev/null
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n "$NS" --create-namespace \
      --set controller.service.type=LoadBalancer \
      --set controller.service.loadBalancerClass=eks.amazonaws.com/nlb \
      --set controller.ingressClassResource.default=false \
      --wait --timeout 10m
    if [ -n "${BASIC_AUTH_USER:-}" ] && [ -n "${BASIC_AUTH_PASSWORD:-}" ]; then
      HASH=$(openssl passwd -apr1 "$BASIC_AUTH_PASSWORD")
      kubectl -n "$NS" create secret generic basic-auth --from-literal=auth="${BASIC_AUTH_USER}:${HASH}" \
        --dry-run=client -o yaml | kubectl apply -f -
      summary "**Basic auth:** secret basic-auth created in ${NS}."
    else
      summary "**Basic auth:** not configured (set BASIC_AUTH_USER and BASIC_AUTH_PASSWORD to enable)."
    fi
    kubectl -n "$NS" get svc ingress-nginx-controller
    summary "**Verified:** ingress-nginx installed."
    ;;
  destroy)
    helm uninstall ingress-nginx -n "$NS" --ignore-not-found || true
    kubectl delete namespace "$NS" --ignore-not-found
    summary "**Removed:** ingress-nginx and its load balancer."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
