#!/usr/bin/env bash
# Stage 03 — EFS shared storage (CloudFormation stack genai-eks-03-efs).
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION VPC_ID

STACK=$(stack_name 03 efs)
TEMPLATE="$(dirname "$0")/template.yaml"

if [ "$ACTION" = destroy ]; then cfn_destroy "$STACK"; exit 0; fi

VPC_CIDR=$(aws ec2 describe-vpcs --region "$AWS_REGION" --vpc-ids "$VPC_ID" \
  --query 'Vpcs[0].CidrBlock' --output text)

# EFS allows one mount target per AZ: pick the first subnet of each AZ.
declare -A SEEN=()
PICK=()
while read -r SUBNET AZ; do
  if [ -z "${SEEN[$AZ]:-}" ]; then SEEN[$AZ]=1; PICK+=("$SUBNET"); fi
done < <(subnets_in_vpc)
[ "${#PICK[@]}" -ge 1 ] || { echo "FAIL: no subnets found in ${VPC_ID}"; exit 1; }
[ "${#PICK[@]}" -le 4 ] || PICK=("${PICK[@]:0:4}")

PARAMS=("VpcId=${VPC_ID}" "VpcCidr=${VPC_CIDR}")
for i in 1 2 3 4; do PARAMS+=("Subnet${i}=${PICK[$((i - 1))]:-}"); done

case "$ACTION" in
  plan)  cfn_plan  "$STACK" "$TEMPLATE" "${PARAMS[@]}" ;;
  apply)
    cfn_apply "$STACK" "$TEMPLATE" "${PARAMS[@]}"
    FS=$(stack_output "$STACK" FileSystemId)
    STATES=$(aws efs describe-mount-targets --region "$AWS_REGION" --file-system-id "$FS" \
      --query 'MountTargets[].LifeCycleState' --output text)
    summary "**Verified:** file system \`${FS}\`, mount targets: ${STATES}"
    ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
