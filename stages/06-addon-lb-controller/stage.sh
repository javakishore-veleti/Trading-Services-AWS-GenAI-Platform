#!/usr/bin/env bash
# Stage 06 — load balancing. EKS Auto Mode includes the load balancer controller, so no Helm chart is
# installed. This stage creates the "alb" IngressClass that Auto Mode watches.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}
require CLUSTER_NAME

case "$ACTION" in
  plan)    summary "Would create IngressClassParams + IngressClass 'alb' (controller eks.amazonaws.com/alb)."
           kubectl apply --dry-run=server -f "$(dirname "$0")/ingressclass.yaml" ;;
  apply)   kubectl apply -f "$(dirname "$0")/ingressclass.yaml"
           kubectl get ingressclass alb
           summary "**Verified:** IngressClass alb is present (Auto Mode load balancing)." ;;
  destroy) kubectl delete ingressclass alb --ignore-not-found
           kubectl delete ingressclassparams.eks.amazonaws.com alb --ignore-not-found
           summary "**Removed:** IngressClass alb. Delete Ingresses before this stage so ALBs are released." ;;
  *) echo "usage: stage.sh plan|apply|destroy"; exit 2 ;;
esac
