"""PostgreSQL 이 접속 가능해질 때까지 기다린다.

컨테이너가 동시에 시작될 때 DB 가 아직 준비되지 않아
'connection refused' 오류로 앱이 죽는 것을 막기 위한 스크립트.
"""

import os
import sys
import time

import psycopg

RETRIES = int(os.environ.get("DB_WAIT_RETRIES", "30"))
DELAY_SECONDS = 2


def main():
    params = {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
        "dbname": os.environ.get("POSTGRES_DB", "todo_db"),
        "user": os.environ.get("POSTGRES_USER", "todo_user"),
        "password": os.environ.get("POSTGRES_PASSWORD", "todo_password"),
        "connect_timeout": 3,
    }
    for attempt in range(1, RETRIES + 1):
        try:
            psycopg.connect(**params).close()
        except psycopg.OperationalError:
            print(f"Waiting for database... ({attempt}/{RETRIES})", flush=True)
            time.sleep(DELAY_SECONDS)
        else:
            print("Database is ready.", flush=True)
            return 0
    print("Database is not available. 접속 정보(POSTGRES_*)를 확인하세요.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
