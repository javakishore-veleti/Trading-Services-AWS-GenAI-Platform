#!/usr/bin/env bash
# Stage 10 — GPU node pool for Auto Mode. Karpenter launches on-demand g6e nodes only when a pod asks for a GPU.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION CLUSTER_NAME

render() {
  cat <<YAML
apiVersion: eks.amazonaws.com/v1
kind: NodeClass
metadata:
  name: gpu
spec:
  role: genai-eks-node-role
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: ${CLUSTER_NAME}
  securityGroupSelectorTerms:
    - tags:
        aws:eks:cluster-name: ${CLUSTER_NAME}
  tags:
    intent: gpu
    cluster: ${CLUSTER_NAME}
---
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu
spec:
  weight: 100
  limits:
    nvidia.com/gpu: 4
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s
  template:
    spec:
      expireAfter: 336h
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: gpu
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: eks.amazonaws.com/instance-family
          operator: In
          values: ["g6e"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: kubernetes.io/os
          operator: In
          values: ["linux"]
      taints:
        - key: nvidia.com/gpu
          value: "true"
          effect: NoSchedule
YAML
}

case "$ACTION" in
  plan)    render | kubectl apply --dry-run=server -f - ;;
  apply)   render | kubectl apply -f -
           kubectl get nodepool gpu
           summary "**Applied:** GPU NodePool 'gpu' (g6e, on-demand). Nodes appear only when a GPU pod is scheduled."
           ;;
  destroy) kubectl delete nodepool gpu --ignore-not-found
           kubectl delete nodeclass gpu --ignore-not-found
           summary "**Removed:** GPU NodePool and NodeClass. Check the EC2 console for leftover GPU instances."
           ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
