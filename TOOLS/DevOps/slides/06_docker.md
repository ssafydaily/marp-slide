---
marp: true
theme: dark-plus-code
paginate: true
style: |
  /* 첫 페이지(lead): 어두운 배경에서 잘 보이도록 밝은 글자색 */
  section.lead h1 {
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  section.lead h2 {
    color: #e3f2fd;
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.3);
    opacity: 1;
  }
  section.lead p {
    color: #cbd5e1;
    opacity: 1;
  }
---

<!-- _class: lead -->

# Step 6. Docker 컨테이너화

## Dockerfile · docker compose · 헬스체크

---

# 학습 목표

- 컨테이너와 이미지의 개념을 설명할 수 있다
- **멀티스테이지 Dockerfile** 로 운영용 이미지를 만든다
- **docker compose** 로 web + PostgreSQL 을 함께 실행한다
- 컨테이너 시작 순서 문제를 **healthcheck + 대기 스크립트**로 해결한다
- 컨테이너 안에서 **pytest** 를 실행한다

📁 실습 폴더: `practice/step06_docker/template`

---

# 왜 컨테이너인가?

```
 개발 PC (Windows)        CI 서버 (Ubuntu)         운영 서버 (EC2)
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ ┌──────────────┐ │    │ ┌──────────────┐ │    │ ┌──────────────┐ │
│ │ todo-api 이미지│ │ =  │ │ todo-api 이미지│ │ =  │ │ todo-api 이미지│ │
│ └──────────────┘ │    │ └──────────────┘ │    │ └──────────────┘ │
│     Docker       │    │     Docker       │    │     Docker       │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

- 앱 + Python + 패키지 + OS 라이브러리를 **하나의 이미지**로 묶음
- 어디서 실행해도 **똑같이** 동작 → "제 PC 에서는 되는데" 해결

---

# 핵심 용어

| 용어 | 설명 | 비유 |
|------|------|------|
| **Image** | 실행에 필요한 모든 것을 담은 읽기 전용 템플릿 | 클래스 |
| **Container** | 이미지를 실행한 프로세스 | 인스턴스 |
| **Dockerfile** | 이미지를 만드는 레시피 | 소스 코드 |
| **Registry** | 이미지 저장소 (Docker Hub, GHCR) | PyPI |
| **Volume** | 컨테이너 밖에 저장되는 데이터 | 외장 디스크 |
| **Compose** | 여러 컨테이너를 한 번에 정의/실행 | 오케스트라 지휘자 |

---

# 완성될 구조

```
docker compose up
        │
        ├── db   : postgres:16-alpine   (volume: pgdata)
        │          healthcheck: pg_isready
        │
        ├── web  : todo-api:local       (port 8000)
        │          entrypoint.sh → wait_for_db → migrate → gunicorn
        │          healthcheck: GET /health/
        │
        └── test : todo-api (test stage) [profile: test]
                   pytest
```

---

# 새로 추가되는 파일

```
step06_docker/solution/
├── Dockerfile            # 이미지 레시피 (builder / runtime / test)
├── .dockerignore         # 이미지에서 제외할 파일
├── docker-compose.yml    # db + web + test
├── entrypoint.sh         # 컨테이너 시작 스크립트
├── scripts/
│   └── wait_for_db.py    # DB 준비 대기
├── .gitattributes        # .sh 파일 줄바꿈(LF) 고정
└── requirements.txt      # + gunicorn, whitenoise
```

---

# 운영용 웹 서버 : gunicorn + whitenoise

```text
# requirements.txt 에 추가
gunicorn>=23.0,<24       # 운영용 WSGI 서버 (runserver 는 개발 전용!)
whitenoise>=6.8,<7       # Django 가 정적 파일을 직접 서빙
```

🛠 **TODO 9** : `config/settings/prod.py`

```python
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

---

# Dockerfile ① builder 단계

```dockerfile
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 🛠 TODO 1 : requirements.txt 만 먼저 복사 → 레이어 캐시 재사용
COPY requirements.txt .
RUN pip install -r requirements.txt
```

<div class="callout tip">
<div class="callout-title">레이어 캐시</div>
코드만 바뀌면 requirements 설치 단계는 <b>캐시를 재사용</b>해 빌드가 수 초 만에 끝납니다.
그래서 <code>COPY . .</code> 보다 requirements 를 먼저 복사합니다.
</div>

---

# Dockerfile ② runtime 단계

```dockerfile
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# root 로 실행하지 않기 (보안)
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
RUN chown appuser:appuser /app

# 🛠 TODO 2 : builder 의 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
# 🛠 TODO 3 : 소스 코드 복사 (appuser 소유)
COPY --chown=appuser:appuser . .
```

<div class="callout warning">
<div class="callout-title">주의</div>
Dockerfile 의 주석은 <b>줄 맨 앞</b>의 <code>#</code> 만 인정됩니다. 명령 뒤에 붙인 <code># ...</code> 는 인자로 해석돼 오류가 납니다.
</div>

- `COPY --from=builder` : 설치 결과(/opt/venv)만 가져옴 → **pip 캐시, 빌드 도구 제외**

---

# Dockerfile ③ 실행 설정

```dockerfile
# Windows CRLF 줄바꿈 제거 → "no such file or directory" 오류 방지
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

USER appuser

# 🛠 TODO 4 : 정적 파일 수집 (빌드 시 DB 불필요, SECRET_KEY 는 임시값)
RUN DJANGO_SECRET_KEY=build-only-secret python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
# 🛠 TODO 5
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--access-logfile", "-"]
```

---

# Dockerfile ④ test 단계

```dockerfile
FROM runtime AS test

ENV DJANGO_SETTINGS_MODULE=config.settings.dev \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

USER root
RUN pip install -r requirements-dev.txt
USER appuser

CMD ["pytest"]
```

- **운영 이미지(runtime)** 에는 pytest 가 없음 → 작고 안전
- **test 이미지** 는 runtime 위에 개발 도구만 추가 → 운영과 **같은 환경**에서 테스트

---

# 멀티스테이지 빌드 정리

```
builder  ──(/opt/venv 복사)──▶  runtime  ──(FROM)──▶  test
pip install                    운영 이미지              + pytest, ruff
(버려짐)                       ★ 배포 대상              CI · 로컬 테스트용
```

```bash
docker build --target runtime -t todo-api:local .
docker images todo-api
```

---

# entrypoint.sh : 컨테이너 시작 스크립트

```sh
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
```

> `exec "$@"` : CMD(gunicorn)가 PID 1 이 되어 **종료 신호를 정상 수신**

---

# 왜 DB 를 기다려야 할까?

```
시간 →
db  : [컨테이너 시작]──[초기화 중...]──────────[접속 가능 ✅]
web : [컨테이너 시작]──[migrate 실행 ❌ connection refused → 종료]
```

**이중 안전장치**

1. compose `depends_on: condition: service_healthy`
   → db 의 healthcheck 가 통과한 뒤 web 시작
2. `scripts/wait_for_db.py`
   → 그래도 접속이 안 되면 2초 간격으로 최대 30회 재시도

---

# scripts/wait_for_db.py

```python
def main():
    params = {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
        ...
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
    return 1
```

---

# 🛠 TODO 6 : .dockerignore

```text
.git
.github
.venv
venv
**/__pycache__
.env            # ⚠️ 비밀정보가 이미지에 들어가지 않도록!
.env.*
!.env.example
.pytest_cache
.ruff_cache
.coverage
htmlcov
staticfiles
deploy
Dockerfile
docker-compose*.yml
```

- 빌드 속도 ↑ (전송할 파일 ↓), 이미지 크기 ↓, **보안** ↑

---

# docker-compose.yml : db

```yaml
name: todo-api

x-db-env: &db-env               # 공통 환경변수 (YAML 앵커)
  POSTGRES_DB: ${POSTGRES_DB:-todo_db}
  POSTGRES_USER: ${POSTGRES_USER:-todo_user}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-todo_password}

services:
  db:
    image: postgres:16-alpine
    environment:
      <<: *db-env
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      retries: 10
```

---

# 🛠 TODO 7 : docker-compose.yml : web

```yaml
  web:
    build:
      context: .
      target: runtime
    image: todo-api:local
    environment:
      <<: *db-env
      POSTGRES_HOST: db                # 컨테이너끼리는 서비스 이름으로 통신
      POSTGRES_PORT: "5432"            # 내부 포트는 항상 5432
      DJANGO_SETTINGS_MODULE: config.settings.prod
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-local-docker-secret-key}
      DJANGO_ALLOWED_HOSTS: localhost,127.0.0.1
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy     # db 가 healthy 가 된 후 시작
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"]
```

---

# 🛠 TODO 8 : docker-compose.yml : test

```yaml
  test:
    build:
      context: .
      target: test
    profiles: ["test"]                 # 평소 up 할 때는 실행되지 않음
    environment:
      <<: *db-env
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      RUN_MIGRATIONS: "false"          # pytest 가 테스트 DB 를 직접 만든다
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

---

# 실행하기

```bash
# Step 1~5 의 compose.db.yml 로 띄운 DB 가 있다면 먼저 종료
docker compose -f compose.db.yml down      # (해당 폴더에서)

docker compose up -d --build
docker compose ps
```

```text
NAME              SERVICE   STATUS                    PORTS
todo-api-db-1     db        Up 20 seconds (healthy)   0.0.0.0:5432->5432/tcp
todo-api-web-1    web       Up 12 seconds (healthy)   0.0.0.0:8000->8000/tcp
```

```bash
curl http://localhost:8000/health/        # {"status": "ok", "database": "ok"}
curl http://localhost:8000/api/todos/
```

---

# 로그 & 컨테이너 내부

```bash
docker compose logs -f web                 # 실시간 로그 (Ctrl+C 로 종료)
```

```text
web-1  | Database is ready.
web-1  | Applying database migrations...
web-1  | [INFO] Starting gunicorn 23.0.0
web-1  | [INFO] Listening at: http://0.0.0.0:8000
```

```bash
docker compose exec web python manage.py createsuperuser   # 관리자 생성
docker compose exec db psql -U todo_user -d todo_db        # DB 접속
todo_db=# \dt                                              # 테이블 목록
```

---

# 컨테이너 안에서 테스트

```bash
docker compose --profile test run --rm test
```

```text
Database is ready.
============================= test session starts ==============================
collected 26 items

tests/test_api.py ..........                                              [ 38%]
tests/test_health.py .                                                    [ 42%]
...
============================== 26 passed in 1.84s ==============================
```

- `--rm` : 실행 후 컨테이너 자동 삭제
- CI 에서도 **같은 방식**으로 검증 가능

---

# 코드 수정 후 반영

```bash
# 코드 수정 → 이미지 다시 빌드 → 컨테이너 교체
docker compose up -d --build web
```

| 명령 | 데이터 |
|------|--------|
| `docker compose stop` | 유지 (컨테이너 정지만) |
| `docker compose down` | 유지 (컨테이너 삭제, 볼륨 유지) |
| `docker compose down -v` | **삭제** (볼륨까지 삭제) |

---

# 🚑 트러블슈팅

| 증상 | 해결 |
|------|------|
| `exec ./entrypoint.sh: no such file or directory` | CRLF 줄바꿈 → Dockerfile 의 `sed` 확인, `.gitattributes` |
| `port is already allocated` (8000) | `runserver` 종료 또는 `"8001:8000"` 으로 변경 |
| `port is already allocated` (5432) | compose.db.yml DB 종료 / `.env` 의 `POSTGRES_PORT` 변경 |
| web 이 `unhealthy` | `docker compose logs web` → ALLOWED_HOSTS, SECRET_KEY 확인 |
| `Database is not available` | db 상태 확인, 비밀번호 변경 시 `down -v` |
| 변경 사항이 반영 안 됨 | `--build` 옵션 빠짐 |

---

# ✅ 체크포인트

- [ ] `docker compose up -d --build` → db, web 모두 **healthy**
- [ ] `http://localhost:8000/health/` 응답 확인
- [ ] `docker compose logs web` 에서 migrate → gunicorn 순서 확인
- [ ] `docker compose --profile test run --rm test` → **26 passed**
- [ ] `docker compose down` 후 다시 up 해도 데이터 유지

---

# 정리

- **이미지** = 실행 환경 전체를 담은 패키지, 어디서나 동일하게 실행
- **멀티스테이지**로 운영 이미지는 작게, 테스트 이미지는 따로
- **compose** 로 여러 서비스와 그 관계(depends_on, healthcheck)를 코드로 정의
- 시작 순서 문제는 **healthcheck + 재시도**로 안전하게

### 다음 시간 ▶ Step 7. CI – GitHub Actions
