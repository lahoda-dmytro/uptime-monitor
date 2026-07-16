#!/bin/bash

# Run this script ONCE on the server after the first deploy to obtain the SSL certificate.
# After that, certbot renews automatically every 12 hours via the certbot container.
#
# Prerequisites:
#   - DNS A record for the domain must point to this server's public IP
#   - Docker containers must be running (docker compose up -d)
#
# Usage: bash scripts/init_ssl.sh

set -e

DOMAIN="uptime-monitor.pp.ua"
EMAIL="ipz235_ldo@student.ztu.edu.ua"
COMPOSE_FILE="/var/www/uptime-monitor/compose/docker-compose.yml"
NGINX_CONF_DIR="/var/www/uptime-monitor/nginx"

echo "Step 1: Switching nginx to HTTP-only config to allow ACME challenge..."
cp "$NGINX_CONF_DIR/default_init.conf" "$NGINX_CONF_DIR/default.conf"
docker compose -f "$COMPOSE_FILE" restart nginx
sleep 2

echo "Step 2: Requesting SSL certificate for $DOMAIN..."
docker exec uptime-certbot certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "Step 3: Restoring full HTTPS nginx config..."
cd /var/www/uptime-monitor && git restore nginx/default.conf
docker compose -f "$COMPOSE_FILE" restart nginx

echo "Done. Verify with: curl -I https://$DOMAIN/health"
