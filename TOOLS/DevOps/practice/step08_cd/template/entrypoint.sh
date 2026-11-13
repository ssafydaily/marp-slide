#!/bin/sh
set -e

# 1) DB 가 접속 가능해질 때까지 대기
python scripts/wait_for_db.py

# 2) 마이그레이션 자동 적용 (RUN_MIGRATIONS=false 로 끌 수 있음)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# 3) CMD 로 전달된 명령 실행 (gunicorn, pytest 등)
exec "$@"
