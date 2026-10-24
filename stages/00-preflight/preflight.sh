#!/usr/bin/env bash
# Stage 00 — read-only preflight. Creates nothing.
# Requires: AWS_REGION, VPC_ID, and AWS credentials in the environment.
set -euo pipefail

: "${AWS_REGION:?AWS_REGION is not set (add it as a repo variable)}"
: "${VPC_ID:?VPC_ID is not set (add it as a repo variable)}"

FAILURES=0
MIN_GPU_VCPUS=4
GPU_QUOTA_NAME="Running On-Demand G and VT instances"

report() {  # report PASS|FAIL message
  local status=$1; shift
  echo "${status}  $*"
  [ "$status" = "FAIL" ] && FAILURES=$((FAILURES + 1))
  return 0
}

summary() {
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then echo "$*" >> "$GITHUB_STEP_SUMMARY"; fi
  echo "$*"
}

# Treat empty output and AWS CLI's "None" as "no value".
clean() { [ "$1" = "None" ] && echo "" || echo "$1"; }

# 1. Credentials ------------------------------------------------------------
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
report PASS "credentials valid (account ${ACCOUNT_ID}, region ${AWS_REGION})"

# 2. VPC exists -------------------------------------------------------------
if ! VPC_CIDR=$(aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --region "$AWS_REGION" \
      --query 'Vpcs[0].CidrBlock' --output text 2>/dev/null); then
  report FAIL "VPC ${VPC_ID} not found in ${AWS_REGION}"
  exit 1
fi
report PASS "VPC ${VPC_ID} found (CIDR ${VPC_CIDR})"

# 3. Subnets, AZs, and routes ----------------------------------------------
MAIN_RT=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
  --filters "Name=vpc-id,Values=${VPC_ID}" "Name=association.main,Values=true" \
  --query 'RouteTables[0].RouteTableId' --output text)

SUBNET_TABLE=$(mktemp)
trap 'rm -f "$SUBNET_TABLE"' EXIT

PUBLIC_COUNT=0
PRIVATE_NAT_COUNT=0
AZS=""

# Read subnets from fd 3 so the AWS CLI calls inside the loop cannot consume them from stdin.
SUBNET_LIST=$(mktemp)
trap 'rm -f "$SUBNET_TABLE" "$SUBNET_LIST"' EXIT
aws ec2 describe-subnets --region "$AWS_REGION" \
  --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query 'Subnets[].[SubnetId,AvailabilityZone]' --output text | tr '\t' ' ' > "$SUBNET_LIST"

while read -r SUBNET_ID AZ <&3; do
  RT=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
    --filters "Name=association.subnet-id,Values=${SUBNET_ID}" \
    --query 'RouteTables[0].RouteTableId' --output text)
  RT=$(clean "$RT")
  [ -z "$RT" ] && RT="$MAIN_RT"   # no explicit association -> main route table

  IGW=$(clean "$(aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$RT" \
    --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0'].GatewayId | [0]" --output text)")
  NAT=$(clean "$(aws ec2 describe-route-tables --region "$AWS_REGION" --route-table-ids "$RT" \
    --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0'].NatGatewayId | [0]" --output text)")

  KIND="isolated"
  if [[ "$IGW" == igw-* ]]; then KIND="public"; PUBLIC_COUNT=$((PUBLIC_COUNT + 1)); fi
  if [[ "$NAT" == nat-* ]]; then KIND="private-nat"; PRIVATE_NAT_COUNT=$((PRIVATE_NAT_COUNT + 1)); fi

  AZS="${AZS} ${AZ}"
  printf '| %s | %s | %s |\n' "$SUBNET_ID" "$AZ" "$KIND" >> "$SUBNET_TABLE"
done 3< "$SUBNET_LIST"

UNIQUE_AZS=$(echo "$AZS" | tr ' ' '\n' | sed '/^$/d' | sort -u | wc -l | tr -d ' ')

summary "### Subnets in ${VPC_ID}"
summary ""
summary "| Subnet | AZ | Routing |"
summary "|---|---|---|"
cat "$SUBNET_TABLE" >> "${GITHUB_STEP_SUMMARY:-/dev/null}" 2>/dev/null || true
cat "$SUBNET_TABLE"
summary ""

if [ "$UNIQUE_AZS" -ge 2 ]; then
  report PASS "subnets span ${UNIQUE_AZS} availability zones"
else
  report FAIL "subnets span ${UNIQUE_AZS} AZ(s); EKS needs at least 2"
fi

if [ "$PUBLIC_COUNT" -ge 1 ]; then
  report PASS "${PUBLIC_COUNT} public subnet(s) with an internet gateway route"
else
  report FAIL "no public subnet (0.0.0.0/0 -> igw). Internet-facing ALBs need one"
fi

if [ "$PRIVATE_NAT_COUNT" -ge 2 ]; then
  report PASS "${PRIVATE_NAT_COUNT} private subnet(s) with a NAT gateway route"
else
  report FAIL "${PRIVATE_NAT_COUNT} private subnet(s) with NAT egress; need >= 2 for EKS nodes"
fi

# 4. GPU vCPU quota ---------------------------------------------------------
GPU_QUOTA=$(aws service-quotas list-service-quotas --service-code ec2 --region "$AWS_REGION" \
  --query "Quotas[?QuotaName=='${GPU_QUOTA_NAME}'].Value | [0]" --output text)
GPU_QUOTA=$(clean "$GPU_QUOTA")

if [ -z "$GPU_QUOTA" ]; then
  report FAIL "could not read quota '${GPU_QUOTA_NAME}'"
elif awk -v q="$GPU_QUOTA" -v m="$MIN_GPU_VCPUS" 'BEGIN { exit !(q >= m) }'; then
  report PASS "GPU quota '${GPU_QUOTA_NAME}' = ${GPU_QUOTA} vCPUs (need >= ${MIN_GPU_VCPUS})"
else
  report FAIL "GPU quota = ${GPU_QUOTA} vCPUs (need >= ${MIN_GPU_VCPUS}). Request an increase before Stage 10"
fi

# 5. Result ----------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  summary "**Preflight failed: ${FAILURES} check(s).** Fix them before Stage 01."
  exit 1
fi
summary "**Preflight passed.** Safe to continue to Stage 01."
