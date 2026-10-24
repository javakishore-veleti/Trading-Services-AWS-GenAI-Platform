#!/usr/bin/env bash
# Stage 19 — GitHub OIDC provider and deploy role (CloudFormation). Creates the role only.
# Switching the workflows from access keys to this role is a separate, deliberate change.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION
STACK=$(stack_name 19 oidc-role)
TEMPLATE="$(dirname "$0")/template.yaml"

case "$ACTION" in
  plan)    cfn_plan "$STACK" "$TEMPLATE" ;;
  apply)
    cfn_apply "$STACK" "$TEMPLATE"
    summary "**Role created:** $(stack_output "$STACK" DeployRoleArn). Workflows still use access keys until switched."
    ;;
  destroy) cfn_destroy "$STACK"; summary "**Removed:** OIDC role and provider." ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
