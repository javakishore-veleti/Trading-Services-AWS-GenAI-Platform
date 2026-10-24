#!/usr/bin/env bash
# Stage 11 — first model: vLLM serving deepseek-r1-qwen3-8b on a GPU node from Stage 10.
# Model weights cache on the EFS claim (Stage 05). Requires the HF_TOKEN GitHub secret.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
MANIFEST="$(dirname "$0")/vllm.yaml"
NS=vllm

case "$ACTION" in
  plan)    kubectl apply --dry-run=server -f "$MANIFEST" ;;
  apply)
    require HF_TOKEN
    kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
    kubectl -n "$NS" create secret generic hf-token --from-literal=token="$HF_TOKEN" \
      --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -f "$MANIFEST"
    summary "Model download takes several minutes on first start. Waiting for readiness (up to 40 min)."
    kubectl -n "$NS" rollout status deployment/deepseek-r1-qwen3-8b --timeout=40m
    summary "**Verified:** deployment ready. Test with: kubectl -n ${NS} port-forward svc/deepseek-r1-qwen3-8b 8000:8000"
    ;;
  destroy)
    kubectl delete namespace "$NS" --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** vLLM namespace. GPU capacity is released when the NodePool drains (Stage 10)."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
