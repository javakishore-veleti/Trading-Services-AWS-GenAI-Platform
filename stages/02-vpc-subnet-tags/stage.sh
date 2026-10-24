#!/usr/bin/env bash
# Stage 02 — tag the existing subnets of VPC_ID so EKS, load balancers and Karpenter can find them.
# Not a CloudFormation stack: CloudFormation cannot tag existing subnets without importing them.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION VPC_ID CLUSTER_NAME

CLUSTER_TAG="kubernetes.io/cluster/${CLUSTER_NAME}"
DISCOVERY_TAG="karpenter.sh/discovery"
summary "### Stage 02 subnet tags ($ACTION) in ${VPC_ID}"

while read -r SUBNET AZ; do
  [ -z "$SUBNET" ] && continue
  if subnet_is_public "$SUBNET"; then KIND=public; else KIND=private; fi
  # Learning mode: nodes run in public subnets, so every subnet gets the discovery tags.
  TAGS="Key=${CLUSTER_TAG},Value=shared Key=${DISCOVERY_TAG},Value=${CLUSTER_NAME}"
  [ "$KIND" = public ] && TAGS="$TAGS Key=kubernetes.io/role/elb,Value=1"
  case "$ACTION" in
    plan)    summary "- ${SUBNET} (${AZ}, ${KIND}): would add ${TAGS}" ;;
    apply)   aws ec2 create-tags --region "$AWS_REGION" --resources "$SUBNET" --tags $TAGS
             summary "- ${SUBNET} (${AZ}, ${KIND}): tagged" ;;
    destroy) aws ec2 delete-tags --region "$AWS_REGION" --resources "$SUBNET" \
               --tags "Key=${CLUSTER_TAG}" "Key=${DISCOVERY_TAG}" "Key=kubernetes.io/role/elb"
             summary "- ${SUBNET} (${AZ}, ${KIND}): tags removed" ;;
    *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
  esac
done < <(subnets_in_vpc)

if [ "$ACTION" = apply ]; then
  N=$(aws ec2 describe-subnets --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:${DISCOVERY_TAG},Values=${CLUSTER_NAME}" \
    --query 'length(Subnets)' --output text)
  summary "**Verified:** ${N} subnet(s) tagged ${DISCOVERY_TAG}=${CLUSTER_NAME}."
fi
