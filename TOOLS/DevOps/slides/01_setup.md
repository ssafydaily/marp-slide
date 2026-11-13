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

# Step 1. 개발 환경 구성

## Django + DRF + PostgreSQL + pytest

---

# 학습 목표

- 가상환경과 `requirements.txt` 로 **재현 가능한 개발 환경**을 만든다
- PostgreSQL 을 **Docker 컨테이너**로 실행한다 (설치 X)
- 접속 정보를 **환경변수(.env)** 로 관리한다
- pytest 로 첫 번째 테스트(`/health/`)를 통과시킨다

📁 실습 폴더: `practice/step01_setup/template`

---

# 왜 "재현 가능한 환경"인가?

- "제 PC 에서는 되는데요" 의 원인 = **환경 차이**
  - Python 버전, 패키지 버전, DB 버전, 설정값
- DevOps 의 첫 단계: **환경을 코드로 기록**

| 대상 | 기록 방법 |
|------|-----------|
| Python 패키지 | `requirements.txt` |
| DB | `compose.db.yml` (Docker) |
| 설정 / 비밀값 | `.env` (+ `.env.example` 공유) |
| 제외 파일 | `.gitignore` |

---

# 프로젝트 구조

```
step01_setup/solution/
├── config/              # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── views.py         # /health/ 뷰
├── tests/
│   └── test_health.py
├── compose.db.yml       # 개발용 PostgreSQL
├── .env.example         # 환경변수 예시
├── .gitignore
├── manage.py
├── pytest.ini
└── requirements.txt
```

---

# 1) 가상환경 만들기

```bash
# 프로젝트 폴더에서
python -m venv .venv

# 활성화
source .venv/Scripts/activate     # Windows (Git Bash)
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/bin/activate         # macOS / Linux

python --version                  # 3.11.x 확인
```

<div class="callout tip">
<div class="callout-title">TIP</div>
VS Code 에서 <code>Ctrl+Shift+P → Python: Select Interpreter</code> 로 .venv 를 선택하세요.
</div>

---

# 2) 패키지 설치 : requirements.txt

```text
Django>=5.2,<5.3
djangorestframework>=3.16,<3.17
psycopg[binary]>=3.2,<4      # PostgreSQL 드라이버 (컴파일 불필요)
python-dotenv>=1.0,<2        # .env 파일 읽기
pytest>=8.3,<9
pytest-django>=4.9,<5
pytest-cov>=6.0,<7
```

```bash
pip install -r requirements.txt
```

- 버전 범위를 지정해 **모두 같은 버전**으로 설치
- `psycopg[binary]` : Windows 에서도 빌드 오류 없이 설치

---

# (참고) 처음부터 만든다면

```bash
pip install django djangorestframework
django-admin startproject config .     # 현재 폴더에 config 프로젝트 생성
pip freeze > requirements.txt          # 설치된 패키지 기록
```

- `config` 라는 이름으로 프로젝트를 만들면 설정 폴더 역할이 명확
- 실습에서는 이미 생성된 template 을 사용합니다

---

# 3) PostgreSQL 을 Docker 로 실행

```yaml
# compose.db.yml
name: todo-api
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-todo_db}
      POSTGRES_USER: ${POSTGRES_USER:-todo_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-todo_password}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
```

---

# compose.db.yml 읽는 법

| 항목 | 의미 |
|------|------|
| `image: postgres:16-alpine` | 공식 PostgreSQL 16 이미지 (설치 불필요) |
| `${POSTGRES_DB:-todo_db}` | `.env` 값 사용, 없으면 기본값 `todo_db` |
| `ports: "5432:5432"` | 내 PC 5432 → 컨테이너 5432 연결 |
| `volumes: pgdata` | 컨테이너를 지워도 **데이터 유지** |
| `healthcheck` | DB 가 접속 가능한지 주기적으로 확인 |

<div class="callout info">
<div class="callout-title">Docker 는 Step 6 에서 자세히!</div>
지금은 "명령 한 줄로 DB 를 띄우는 도구" 정도로 이해하면 충분합니다.
</div>

---

# DB 실행 & 상태 확인

```bash
cp .env.example .env                       # 환경변수 파일 생성

docker compose -f compose.db.yml up -d     # 백그라운드 실행
docker compose -f compose.db.yml ps        # 상태 확인
```

```text
NAME              IMAGE                STATUS
todo-api-db-1     postgres:16-alpine   Up 10 seconds (healthy)
```

- **`(healthy)`** 가 보이면 접속 준비 완료
- `(health: starting)` 이면 몇 초 기다렸다 다시 확인

---

# 4) 환경변수 : .env

```bash
# .env.example  →  복사해서 .env 로 사용
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-dev-only-key

POSTGRES_DB=todo_db
POSTGRES_USER=todo_user
POSTGRES_PASSWORD=todo_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

- 비밀번호 · 키를 **코드에 직접 쓰지 않는다**
- `.env` 는 `.gitignore` 에 등록 → **커밋 금지**
- 팀원에게는 `.env.example` 로 형식만 공유

---

# settings.py : .env 읽기

```python
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 프로젝트 루트의 .env 파일을 환경변수로 읽어온다 (없어도 오류 없음)
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
```

---

# 🛠 TODO 1 : DATABASES 설정

`config/settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "todo_db"),
        "USER": os.environ.get("POSTGRES_USER", "todo_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "todo_password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {"connect_timeout": 5},
    }
}
```

> 기본값을 `compose.db.yml` 과 **똑같이** 맞춰두면 `.env` 가 없어도 동작

---

# 마이그레이션 & 접속 확인

```bash
python manage.py migrate
```

```text
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  ...
```

```bash
python manage.py runserver
# http://127.0.0.1:8000/admin/ 접속 확인
```

---

# 5) pytest 설정 : pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
testpaths = tests
python_files = test_*.py
addopts = -ra
```

- `pytest-django` 가 Django 설정을 로드해 줌
- `testpaths` : 테스트를 찾을 폴더
- 테스트 실행 시 **`test_todo_db` 라는 별도 DB 를 자동 생성/삭제**
  → 개발 데이터와 섞이지 않음

---

# 첫 번째 테스트 : /health/

`tests/test_health.py`

```python
import pytest


@pytest.mark.django_db
def test_health_returns_ok(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
```

- `client` : pytest-django 가 제공하는 테스트용 HTTP 클라이언트 (fixture)
- `@pytest.mark.django_db` : 이 테스트는 DB 를 사용함

---

# 🔴 Red : 먼저 실패를 확인

```bash
pytest
```

```text
FAILED tests/test_health.py::test_health_returns_ok - assert 404 == 200
```

<div class="callout tip">
<div class="callout-title">왜 실패부터?</div>
테스트가 <b>정말로 기능을 검사하는지</b> 확인하기 위해서입니다.
처음부터 통과하는 테스트는 아무것도 검증하지 않을 수 있어요.
</div>

---

# 🛠 TODO 2 : 헬스체크 뷰

`config/views.py`

```python
from django.db import DatabaseError, connection
from django.http import JsonResponse


def health(request):
    """서버와 DB 상태를 확인하는 헬스체크 엔드포인트."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "error"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
```

> 운영 단계에서 Docker · Nginx · 배포 스크립트가 이 URL 로 **서버 상태를 확인**합니다

---

# 🛠 TODO 3 : URL 연결

`config/urls.py`

```python
from django.contrib import admin
from django.urls import path

from config.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
]
```

---

# 🟢 Green : 테스트 통과

```bash
pytest -v
```

```text
tests/test_health.py::test_health_returns_ok PASSED          [100%]
============================ 1 passed in 0.52s ============================
```

```bash
python manage.py runserver
curl http://127.0.0.1:8000/health/
# {"status": "ok", "database": "ok"}
```

---

# .gitignore : 커밋하지 않을 것

```gitignore
# Python
__pycache__/
.venv/

# 환경변수 (비밀정보)
.env

# Django
staticfiles/

# Test / Coverage
.pytest_cache/
.coverage
htmlcov/
```

<div class="callout warning">
<div class="callout-title">주의</div>
<code>.env</code> 를 한 번이라도 커밋하면 Git 기록에 남습니다. 비밀번호는 즉시 교체해야 합니다.
</div>

---

# 🚑 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `connection refused` | DB 컨테이너 미실행 → `docker compose -f compose.db.yml ps` |
| `port is already allocated` | 5432 사용 중 → `.env` 에 `POSTGRES_PORT=5433` 후 `up -d` |
| `password authentication failed` | 예전 볼륨의 비밀번호 → `down -v` 후 다시 `up -d` |
| `permission denied to create database` | 테스트 DB 생성 권한 → 공식 이미지 기본 사용자 사용 |
| `docker: command not found` | Docker Desktop 실행 확인 |

```bash
docker compose -f compose.db.yml down -v   # DB 초기화 (데이터 삭제)
docker compose -f compose.db.yml up -d
```

---

# ✅ 체크포인트

- [ ] `.venv` 활성화 & `pip install -r requirements.txt`
- [ ] `docker compose -f compose.db.yml ps` → **healthy**
- [ ] `python manage.py migrate` 성공
- [ ] `pytest` → **1 passed**
- [ ] 브라우저에서 `/health/` 응답 확인
- [ ] `.env` 가 `.gitignore` 에 포함되어 있음

---

# 정리

- 환경을 **파일로 기록**: `requirements.txt`, `compose.db.yml`, `.env.example`
- PostgreSQL 은 Docker 로 실행 → 설치 없이 모두 같은 버전
- 설정은 **환경변수**, 비밀값은 **커밋 금지**
- 테스트는 **Red → Green** 순서로

### 다음 시간 ▶ Step 2. TDD & pytest 기초
