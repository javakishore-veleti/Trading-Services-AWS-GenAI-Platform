#!/usr/bin/env bash
# Create one database, schema, and HNSW index per team on the pgvector server.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

echo "Creating one pgvector database per team..."
python3 "$LOCAL_DIR/pgvector/provision.py" "$ROOT/.env"
