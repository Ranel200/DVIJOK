#!/bin/sh
set -eu

DEPLOY_DIR=${DEPLOY_DIR:-/opt/dvizhok/deploy}
BACKUP_DIR=${BACKUP_DIR:-/opt/dvizhok/backups/postgres}
RETENTION_DAYS=${RETENTION_DAYS:-14}

cd "$DEPLOY_DIR"
set -a
. ./.env.production
set +a

mkdir -p "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
temporary="$BACKUP_DIR/.dvizhok-$timestamp.sql.gz.part"
target="$BACKUP_DIR/dvizhok-$timestamp.sql.gz"

docker compose --env-file .env.production -f compose.prod.yml exec -T db \
    pg_dump --clean --if-exists --no-owner --no-privileges \
    -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip -9 > "$temporary"
mv "$temporary" "$target"
find "$BACKUP_DIR" -type f -name 'dvizhok-*.sql.gz' -mtime "+$RETENTION_DAYS" -delete

echo "$target"
