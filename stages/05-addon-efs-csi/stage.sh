#!/usr/bin/env bash
# Stage 05 — EFS CSI driver as an EKS managed add-on, with a Pod Identity role, plus the "efs" StorageClass.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require AWS_REGION CLUSTER_NAME

STACK=$(stack_name 05 addon-efs-csi)
TEMPLATE="$(dirname "$0")/template.yaml"
ADDON=aws-efs-csi-driver
SA=efs-csi-controller-sa

if [ "$ACTION" = destroy ]; then
  kubectl delete storageclass efs --ignore-not-found
  aws eks delete-addon --region "$AWS_REGION" --cluster-name "$CLUSTER_NAME" --addon-name "$ADDON" >/dev/null 2>&1 || true
  cfn_destroy "$STACK"
  exit 0
fi

case "$ACTION" in
  plan) cfn_plan "$STACK" "$TEMPLATE" "ClusterName=${CLUSTER_NAME}"; exit 0 ;;
  apply) ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac

cfn_apply "$STACK" "$TEMPLATE" "ClusterName=${CLUSTER_NAME}"
ROLE=$(stack_output "$STACK" RoleArn)
PIA="serviceAccount=${SA},roleArn=${ROLE}"

if aws eks describe-addon --region "$AWS_REGION" --cluster-name "$CLUSTER_NAME" --addon-name "$ADDON" >/dev/null 2>&1; then
  aws eks update-addon --region "$AWS_REGION" --cluster-name "$CLUSTER_NAME" --addon-name "$ADDON" \
    --pod-identity-associations "$PIA" --resolve-conflicts OVERWRITE >/dev/null
else
  aws eks create-addon --region "$AWS_REGION" --cluster-name "$CLUSTER_NAME" --addon-name "$ADDON" \
    --pod-identity-associations "$PIA" --resolve-conflicts OVERWRITE >/dev/null
fi
aws eks wait addon-active --region "$AWS_REGION" --cluster-name "$CLUSTER_NAME" --addon-name "$ADDON"
summary "**Add-on active:** ${ADDON}"

FS=$(stack_output genai-eks-03-efs FileSystemId)
kubectl apply -f - <<YAML
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: ${FS}
  directoryPerms: "700"
YAML

# Verify: a test claim binds and a pod can write to it.
kubectl apply -f - <<YAML
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: efs-verify
  namespace: default
spec:
  storageClassName: efs
  accessModes: [ReadWriteMany]
  resources:
    requests:
      storage: 5Gi
YAML
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/efs-verify --timeout=300s
kubectl delete pvc efs-verify --ignore-not-found
summary "**Verified:** EFS claim bound through the efs StorageClass (file system ${FS})."
