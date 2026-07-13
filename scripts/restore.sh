#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$ROOT_DIR/.env" ]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
else
    echo "error: .env file not found in $ROOT_DIR"
    exit 1
fi

CONTAINER_NAME="uptime-postgres"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "error: database container '$CONTAINER_NAME' is not running"
    exit 1
fi

BACKUP_DIR="$ROOT_DIR/backups"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "error: backup directory $BACKUP_DIR does not exist"
    exit 1
fi

BACKUPS=($(ls -1t "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || true))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo "error: no backup files found in $BACKUP_DIR"
    exit 1
fi

if [ -z "$1" ]; then
    echo "available backups:"
    for i in "${!BACKUPS[@]}"; do
        echo "$((i+1))) $(basename "${BACKUPS[$i]}")"
    done
    
    read -p "select a backup to restore (1-${#BACKUPS[@]}): " CHOICE
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#BACKUPS[@]}" ]; then
        echo "error: invalid selection"
        exit 1
    fi
    SELECTED_BACKUP="${BACKUPS[$((CHOICE-1))]}"
else
    SELECTED_BACKUP="$1"
    if [ ! -f "$SELECTED_BACKUP" ]; then
        echo "error: backup file '$SELECTED_BACKUP' not found"
        exit 1
    fi
fi

echo "WARNING: this will overwrite the current database"
read -p "are you sure you want to proceed? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[yY]$ ]]; then
    echo "restore cancelled"
    exit 0
fi

echo "restoring database from $(basename "$SELECTED_BACKUP")..."
if gunzip -c "$SELECTED_BACKUP" | docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"; then
    echo "database successfully restored"
else
    echo "error: database restore failed"
    exit 1
fi
