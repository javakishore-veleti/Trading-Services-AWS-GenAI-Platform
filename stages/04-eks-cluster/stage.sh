#!/usr/bin/env bash
# Stage 04 — EKS cluster in Auto Mode (CloudFormation stack genai-eks-04-eks-cluster).
# Learning mode: nodes use the public subnets of the VPC; no NAT gateway.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION VPC_ID CLUSTER_NAME

STACK=$(stack_name 04 eks-cluster)
TEMPLATE="$(dirname "$0")/template.yaml"
K8S_VERSION=${K8S_VERSION:-1.34}

if [ "$ACTION" = destroy ]; then cfn_destroy "$STACK"; exit 0; fi

# EKS cannot place the control plane in every zone. us-east-1e is rejected, so skip it.
SUBNETS=$(subnets_in_vpc | awk '$2 != "us-east-1e" {print $1}' | paste -sd, -)
CI_ARN=$(aws sts get-caller-identity --query Arn --output text)
PARAMS=("ClusterName=${CLUSTER_NAME}" "KubernetesVersion=${K8S_VERSION}" "SubnetIds=${SUBNETS}" "CiPrincipalArn=${CI_ARN}")

case "$ACTION" in
  plan) cfn_plan "$STACK" "$TEMPLATE" "${PARAMS[@]}" ;;
  apply)
    cfn_apply "$STACK" "$TEMPLATE" "${PARAMS[@]}"
    STATUS=$(aws eks describe-cluster --region "$AWS_REGION" --name "$CLUSTER_NAME" \
      --query 'cluster.status' --output text)
    summary "**Cluster status:** ${STATUS}"
    aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
    summary "**Verified node pools:**"
    kubectl get nodepools --request-timeout=60s | tee -a "${GITHUB_STEP_SUMMARY:-/dev/null}"
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
