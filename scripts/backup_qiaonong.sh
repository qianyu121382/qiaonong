#!/usr/bin/env bash
set -euo pipefail

: "${QIAONONG_BACKUP_DIR:?请设置巧侬独立备份目录}"
: "${QIAONONG_DB_NAME:?请设置巧侬数据库名}"
: "${QIAONONG_DB_USER:?请设置巧侬数据库角色}"
: "${QIAONONG_MEDIA_DIR:?请设置巧侬媒体目录}"

if [[ "$QIAONONG_BACKUP_DIR" == "/" || "$QIAONONG_MEDIA_DIR" == "/" ]]; then
  printf '拒绝使用根目录作为备份或媒体目录。\n' >&2
  exit 2
fi
if [[ ! -d "$QIAONONG_MEDIA_DIR" ]]; then
  printf '媒体目录不存在：%s\n' "$QIAONONG_MEDIA_DIR" >&2
  exit 2
fi

umask 077
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
destination="${QIAONONG_BACKUP_DIR%/}/${timestamp}"
mkdir -p -- "$destination"

pg_dump \
  --format=custom \
  --file="$destination/database.dump" \
  --host="${QIAONONG_DB_HOST:-127.0.0.1}" \
  --port="${QIAONONG_DB_PORT:-5432}" \
  --username="$QIAONONG_DB_USER" \
  "$QIAONONG_DB_NAME"

tar --create --gzip --file="$destination/media.tar.gz" \
  --directory="$(dirname -- "$QIAONONG_MEDIA_DIR")" \
  "$(basename -- "$QIAONONG_MEDIA_DIR")"

printf '%s\n' "${QIAONONG_DEPLOY_COMMIT:-unknown}" > "$destination/commit.txt"
printf '巧侬备份完成：%s\n' "$destination"
