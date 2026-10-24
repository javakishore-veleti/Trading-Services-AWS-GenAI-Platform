#!/usr/bin/env bash
# Shared helpers for stage scripts. Sourced by stages/NN-*/stage.sh, never executed directly.
set -euo pipefail

require() {  # require VAR1 VAR2 ... — fail if any is unset or empty
  local v
  for v in "$@"; do
    if [ -z "${!v:-}" ]; then echo "FAIL: ${v} is not set" >&2; exit 1; fi
  done
}

summary() {  # write to the job summary and stdout
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then echo "$*" >> "$GITHUB_STEP_SUMMARY"; fi
  echo "$*"
}

stack_name() {  # stack_name 03 efs  ->  genai-eks-03-efs
  echo "genai-eks-$1-$2"
}

stack_exists() {  # stack_exists STACK
  aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$1" >/dev/null 2>&1
}

stack_output() {  # stack_output STACK OUTPUT_KEY
  aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$1" \
    --query "Stacks[0].Outputs[?OutputKey=='$2'].OutputValue" --output text
}

subnets_in_vpc() {  # prints "subnet-id az" per line
  aws ec2 describe-subnets --region "$AWS_REGION" --filters "Name=vpc-id,Values=${VPC_ID}" \
    --query 'Subnets[].[SubnetId,AvailabilityZone]' --output text
}

subnet_is_public() {  # subnet_is_public SUBNET_ID — true if its default route targets an internet gateway
  local rt igw
  rt=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
    --filters "Name=association.subnet-id,Values=$1" --query 'RouteTables[0].RouteTableId' --output text)
  if [ -z "$rt" ] || [ "$rt" = "None" ]; then
    rt=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
      --filters "Name=vpc-id,Values=${VPC_ID}" "Name=association.main,Values=true" \
      --query 'RouteTables[0].RouteTableId' --output text)
  fi
  igw=$(aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$rt" \
    --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0'].GatewayId | [0]" --output text)
  [[ "$igw" == igw-* ]]
}

# cfn_plan STACK TEMPLATE [Key=Value ...] — create a change set, show it, delete it. Changes nothing.
cfn_plan() {
  local stack=$1 template=$2; shift 2
  local type=CREATE cs="plan-$(date +%s)" params=() p line reason
  stack_exists "$stack" && type=UPDATE
  for p in "$@"; do params+=("ParameterKey=${p%%=*},ParameterValue=${p#*=}"); done
  aws cloudformation create-change-set --region "$AWS_REGION" --stack-name "$stack" \
    --change-set-name "$cs" --change-set-type "$type" --template-body "file://$template" \
    --capabilities CAPABILITY_NAMED_IAM --parameters "${params[@]}" >/dev/null
  if ! aws cloudformation wait change-set-create-complete --region "$AWS_REGION" \
      --stack-name "$stack" --change-set-name "$cs" 2>/dev/null; then
    reason=$(aws cloudformation describe-change-set --region "$AWS_REGION" --stack-name "$stack" \
      --change-set-name "$cs" --query StatusReason --output text)
    summary "No changes for \`$stack\`: ${reason}"
    aws cloudformation delete-change-set --region "$AWS_REGION" --stack-name "$stack" --change-set-name "$cs" || true
    return 0
  fi
  summary "### Change set for \`$stack\` ($type)"
  aws cloudformation describe-change-set --region "$AWS_REGION" --stack-name "$stack" --change-set-name "$cs" \
    --query 'Changes[].ResourceChange.[Action,LogicalResourceId,ResourceType]' --output text \
    | while IFS=$'\t' read -r line; do summary "- ${line}"; done
  aws cloudformation delete-change-set --region "$AWS_REGION" --stack-name "$stack" --change-set-name "$cs"
}

# cfn_apply STACK TEMPLATE [Key=Value ...] — create or update the stack.
cfn_apply() {
  local stack=$1 template=$2; shift 2
  aws cloudformation deploy --region "$AWS_REGION" --stack-name "$stack" --template-file "$template" \
    --capabilities CAPABILITY_NAMED_IAM --no-fail-on-empty-changeset --parameter-overrides "$@"
  summary "**Applied** stack \`$stack\`."
}

# cfn_destroy STACK — delete the stack and wait for it to finish.
cfn_destroy() {
  local stack=$1
  if ! stack_exists "$stack"; then summary "Stack \`$stack\` not present; nothing to delete."; return 0; fi
  aws cloudformation delete-stack --region "$AWS_REGION" --stack-name "$stack"
  aws cloudformation wait stack-delete-complete --region "$AWS_REGION" --stack-name "$stack"
  summary "**Deleted** stack \`$stack\`."
}
