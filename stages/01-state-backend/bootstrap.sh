#!/usr/bin/env bash
# Stage 01 — Terraform remote state bucket.
# Usage: bootstrap.sh plan|apply
# plan  : read-only, prints what would change
# apply : creates the bucket if missing and enforces versioning, encryption, no public access
set -euo pipefail

MODE="${1:-plan}"
: "${AWS_REGION:?AWS_REGION is not set}"
case "$MODE" in plan|apply) ;; *) echo "usage: $0 plan|apply"; exit 2 ;; esac

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
# Same formula every stage uses, so no variable needs to be stored.
BUCKET="genai-eks-tfstate-${ACCOUNT_ID}"

summary() {
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then echo "$*" >> "$GITHUB_STEP_SUMMARY"; fi
  echo "$*"
}

if aws s3api head-bucket --bucket "$BUCKET" >/dev/null 2>&1; then
  EXISTS=true
else
  EXISTS=false
fi

summary "### Terraform state bucket"
summary ""
summary "- Bucket: \`${BUCKET}\`"
summary "- Region: \`${AWS_REGION}\`"
summary "- Exists now: \`${EXISTS}\`"
summary ""

if [ "$MODE" = "plan" ]; then
  if [ "$EXISTS" = "true" ]; then
    echo "Bucket exists. Apply would only re-assert versioning, encryption and public-access-block."
  else
    echo "Apply would create bucket ${BUCKET} with versioning, SSE-S3 and public access blocked."
  fi
  exit 0
fi

# ---- apply ----
if [ "$EXISTS" = "false" ]; then
  if [ "$AWS_REGION" = "us-east-1" ]; then
    # us-east-1 must NOT send a LocationConstraint; other regions must.
    aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION"
  else
    aws s3api create-bucket --bucket "$BUCKET" --region "$AWS_REGION" \
      --create-bucket-configuration "LocationConstraint=${AWS_REGION}"
  fi
  echo "created ${BUCKET}"
fi

aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"},"BucketKeyEnabled":true}]}'

VERSIONING=$(aws s3api get-bucket-versioning --bucket "$BUCKET" --query Status --output text)
[ "$VERSIONING" = "Enabled" ] || { echo "FAIL: versioning is ${VERSIONING}"; exit 1; }

summary "**Verified:** versioning \`${VERSIONING}\`, SSE-S3 on, public access blocked."
summary ""
summary "Every later stage backend uses bucket \`${BUCKET}\` with \`use_lockfile = true\`."
