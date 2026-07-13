#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "starting deployment..."

if [ ! -f "$ROOT_DIR/.env" ]; then
    echo "error: .env file not found in $ROOT_DIR. deployment aborted"
    exit 1
fi

echo "pulling latest code from repository..."
git pull origin main || {
    echo "warning: git pull failed, continuing deployment with local code"
}

echo "rebuilding and starting docker containers..."
docker compose -f "$ROOT_DIR/compose/docker-compose.yml" up -d --build

echo "running integration healthcheck..."
if bash "$ROOT_DIR/scripts/healthcheck.sh"; then
    echo "deployment successfully completed"
else
    echo "error: healthcheck failed after deployment"
    exit 1
fi
