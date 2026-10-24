#!/usr/bin/env bash
# Stage 17 — Strands calculator agent (FastAPI) calling the model through LiteLLM. Image from Stage 16.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
NS=agent
IMAGE_REPO=$(stack_output genai-eks-16-ecr-and-build RepositoryUri 2>/dev/null || echo "")

render() {
  cat <<YAML
apiVersion: v1
kind: Namespace
metadata:
  name: ${NS}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: calculator-agent
  namespace: ${NS}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: calculator-agent
  template:
    metadata:
      labels:
        app: calculator-agent
    spec:
      automountServiceAccountToken: false
      containers:
        - name: agent
          image: ${IMAGE_REPO}:latest
          env:
            - name: USE_BEDROCK
              value: "false"
            - name: LITELLM_BASE_URL
              value: http://litellm.litellm.svc.cluster.local:4000
            - name: LITELLM_MODEL_NAME
              value: deepseek-r1-qwen3-8b
            - name: LITELLM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: litellm-key
                  key: LITELLM_MASTER_KEY
            - name: USE_MCP_TOOLS
              value: "false"
            - name: USE_MCP_GATEWAY
              value: "false"
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: calculator-agent
  namespace: ${NS}
spec:
  selector:
    app: calculator-agent
  ports:
    - port: 80
      targetPort: 80
YAML
}

case "$ACTION" in
  plan)    render | kubectl apply --dry-run=server -f - ;;
  apply)
    [ -n "$IMAGE_REPO" ] || { echo "FAIL: stage 16 has no ECR repository yet"; exit 1; }
    kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
    # Copy the LiteLLM key into the agent namespace.
    ensure_secret litellm litellm-key LITELLM_MASTER_KEY
    kubectl -n litellm get secret litellm-key -o yaml | sed "s/namespace: litellm/namespace: ${NS}/" | kubectl apply -f -
    render | kubectl apply -f -
    kubectl -n "$NS" rollout status deployment/calculator-agent --timeout=10m
    CODE=$(in_cluster_curl "$NS" http://calculator-agent.${NS}.svc.cluster.local/docs -o /dev/null -w '%{http_code}' || true)
    summary "**Verified:** agent rollout complete (/docs returned ${CODE})."
    ;;
  destroy)
    kubectl delete namespace "$NS" --ignore-not-found --wait=true --timeout=10m
    summary "**Removed:** agent namespace."
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
