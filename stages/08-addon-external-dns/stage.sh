#!/usr/bin/env bash
# Stage 08 — ExternalDNS (optional). Needs a Route 53 hosted zone and a DOMAIN value.
# Without DOMAIN the stage is skipped on purpose; the course uses per-service ALB hostnames instead.
# Usage: stage.sh plan|apply|destroy
source "$(dirname "$0")/../../scripts/lib.sh"
ACTION=${1:?usage: stage.sh plan|apply|destroy}

if [ -z "${DOMAIN:-}" ]; then
  summary "**Stage 08 skipped:** no DOMAIN set (optional stage; needs a Route 53 hosted zone)."
  exit 0
fi
summary "**Stage 08 not implemented yet** for DOMAIN=${DOMAIN}. Add the Route 53 role stack and the external-dns chart here."
exit 1
