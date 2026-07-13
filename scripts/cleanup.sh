#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$ROOT_DIR/backups"

if [ -d "$BACKUP_DIR" ]; then
    BACKUPS_TO_REMOVE=$(ls -1t "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | tail -n +6 || true)
    if [ -n "$BACKUPS_TO_REMOVE" ]; then
        echo "removing old database backups..."
        echo "$BACKUPS_TO_REMOVE" | xargs rm -f
        echo "cleanup completed"
    else
        echo "no old backups to clean up (5 or fewer backups exist)"
    fi
else
    echo "backup directory does not exist, skipping database backup cleanup"
fi

echo "cleaning up unused docker assets..."
docker system prune -f
