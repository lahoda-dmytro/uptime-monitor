#!/bin/bash

# Run this script ONCE after the first deploy to obtain the SSL certificate.
# After that, certbot renews automatically every 12 hours via the certbot container.

set -e

DOMAIN="uptime-monitor.pp.ua"
EMAIL="ipz235_ldo@student.ztu.edu.ua"
COMPOSE_FILE="/var/www/uptime-monitor/compose/docker-compose.yml"

echo "Requesting SSL certificate for $DOMAIN..."

docker compose -f "$COMPOSE_FILE" run --rm certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "Certificate obtained. Reloading nginx..."
docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload

echo "Done. Visit https://$DOMAIN to verify."
