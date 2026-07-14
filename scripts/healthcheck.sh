#!/bin/bash

set -e

CONTAINERS=("uptime-postgres" "uptime-app" "uptime-nginx")

echo "checking containers status..."
for c in "${CONTAINERS[@]}"; do
    if ! docker ps --format '{{.Names}}' | grep -q "^$c$"; then
        echo "error: container '$c' is not running"
        exit 1
    fi
done
echo "all containers are running"

echo "checking API health endpoint..."
HTTP_STATUS=$(curl -sk https://localhost/health -o /dev/null -w "%{http_code}" || true)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "healthcheck passed: API is healthy and reachable through nginx"
else
    echo "error: healthcheck failed, HTTP status code: $HTTP_STATUS"
    exit 1
fi
