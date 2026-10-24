#!/usr/bin/env bash
# Stage 16 — ECR repository (CloudFormation) and an image build of the agent source from Stage 17.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION
STACK=$(stack_name 16 ecr-and-build)
TEMPLATE="$(dirname "$0")/template.yaml"
APP="$(dirname "$0")/../17-strands-calculator-agent/app"

if [ "$ACTION" = destroy ]; then
  # Delete the images first; a non-empty repository cannot be removed by the stack.
  aws ecr batch-delete-image --region "$AWS_REGION" --repository-name genai-eks-agent \
    --image-ids "$(aws ecr list-images --region "$AWS_REGION" --repository-name genai-eks-agent --query 'imageIds' --output json)" \
    >/dev/null 2>&1 || true
  cfn_destroy "$STACK"
  exit 0
fi

case "$ACTION" in
  plan) cfn_plan "$STACK" "$TEMPLATE"; exit 0 ;;
  apply) ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac

cfn_apply "$STACK" "$TEMPLATE"
URI=$(stack_output "$STACK" RepositoryUri)
REGISTRY=${URI%%/*}
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
SHA=$(git rev-parse --short HEAD 2>/dev/null || echo manual)
docker build --platform linux/amd64 -t "${URI}:${SHA}" -t "${URI}:latest" "$APP"
docker push "${URI}:${SHA}"
docker push "${URI}:latest"
COUNT=$(aws ecr describe-images --region "$AWS_REGION" --repository-name genai-eks-agent --query 'length(imageDetails)' --output text)
summary "**Verified:** ${URI}:latest pushed (${COUNT} image(s) in the repository)."
