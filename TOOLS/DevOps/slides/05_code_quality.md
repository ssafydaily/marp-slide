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

# Step 5. 코드 품질 자동화

## ruff · pre-commit · 설정 분리

---

# 학습 목표

- **ruff** 로 린트(lint)와 포맷(format)을 자동화한다
- **pre-commit** 으로 커밋 전에 검사를 강제한다
- Django 설정을 **base / dev / prod** 로 분리한다
- 운영 / 개발 의존성을 **requirements 분리**로 관리한다

📁 실습 폴더: `practice/step05_quality/template`

---

# 왜 자동화된 품질 검사인가?

- 코드 리뷰에서 "따옴표 통일해 주세요", "import 순서…" → **시간 낭비**
- 사람마다 스타일이 다르면 diff 가 지저분해짐
- 사용하지 않는 import, `== None` 같은 **실수**는 도구가 더 잘 찾는다

<div class="callout tip">
<div class="callout-title">원칙</div>
기계가 할 수 있는 검사는 기계에게. 사람의 리뷰는 <b>설계와 로직</b>에 집중.
</div>

---

# ruff 란?

- Rust 로 작성된 **초고속** Python 린터 + 포매터
- flake8, isort, black, pyupgrade 등을 **하나로 대체**

| 명령 | 역할 |
|------|------|
| `ruff check .` | 문제 찾기 (lint) |
| `ruff check --fix .` | 자동 수정 가능한 것 고치기 |
| `ruff format .` | 코드 포맷 통일 (black 호환) |
| `ruff format --check .` | 포맷 검사만 (CI 용) |

---

# requirements 분리

<div class="cols">
<div>

`requirements.txt` (운영)

```text
Django>=5.2,<5.3
djangorestframework>=3.16,<3.17
psycopg[binary]>=3.2,<4
python-dotenv>=1.0,<2
```

</div>
<div>

`requirements-dev.txt` (개발)

```text
-r requirements.txt
pytest>=8.3,<9
pytest-django>=4.9,<5
pytest-cov>=6.0,<7
ruff>=0.8
pre-commit>=4.0,<5
```

</div>
</div>

```bash
pip install -r requirements-dev.txt
```

> 운영 이미지(Step 6)에는 테스트 도구를 넣지 않아 **가볍고 안전**

---

# 🛠 TODO 5 : ruff 설정 (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["**/migrations/**"]

[tool.ruff.lint]
# E/W: 스타일, F: 버그 가능성, I: import 정렬, B: 흔한 실수, UP: 최신 문법, DJ: Django
select = ["E", "W", "F", "I", "B", "UP", "DJ"]

[tool.ruff.lint.isort]
known-first-party = ["config", "todos"]

[tool.ruff.format]
quote-style = "double"
```

---

# 🛠 TODO 7 : ruff 로 코드 정리

template 의 `todos/views.py` 는 일부러 지저분하게 작성되어 있습니다.

```bash
ruff check .
```

```text
I001 Import block is un-sorted or un-formatted   --> todos/views.py:1:1
F401 `os` imported but unused                    --> todos/views.py:1:8
E711 Comparison to `None` should be `cond is not None`  --> todos/views.py:15:23
Found 3 errors.
[*] 2 fixable with the `--fix` option.
```

```bash
ruff check --fix .     # I001, F401 자동 수정
# E711 은 직접 수정:  if is_done != None  →  if is_done is not None
ruff format .          # 따옴표, 빈 줄, 들여쓰기 통일
```

---

# ruff format 전 / 후

<div class="cols">
<div>

**Before**

```python
    serializer_class = TodoSerializer
    def get_queryset(self):
        is_done = self.request \
            .query_params.get('is_done')
```

</div>
<div>

**After**

```python
    serializer_class = TodoSerializer

    def get_queryset(self):
        is_done = self.request.query_params.get("is_done")
```

</div>
</div>

- 포맷은 **토론 대상이 아니다** → 도구가 정한 대로

---

# pre-commit : 커밋 전 자동 검사

```
git commit
    │
    ▼
pre-commit 훅 실행 ──▶ ruff check --fix ──▶ ruff format ──▶ 기타 검사
    │                                                         │
    ├── 모두 통과 → 커밋 완료                                   │
    └── 실패 / 파일 수정됨 → 커밋 중단 (수정 사항 확인 후 다시 커밋) ◀┘
```

- 나쁜 코드가 **저장소에 들어가기 전에** 차단
- 팀원 모두 같은 검사를 자동으로 실행

---

# 🛠 TODO 6 : .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace     # 줄 끝 공백 제거
      - id: end-of-file-fixer       # 파일 끝 개행
      - id: check-yaml              # YAML 문법 검사
      - id: check-added-large-files # 큰 파일 커밋 방지
      - id: detect-private-key      # 개인키 커밋 방지

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

# pre-commit 사용하기

```bash
pre-commit install                # git hook 등록 (저장소마다 1회)
pre-commit run --all-files        # 전체 파일 검사
```

```text
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
detect private key.......................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
```

<div class="callout warning">
<div class="callout-title">주의</div>
<code>.pre-commit-config.yaml</code> 은 <b>Git 저장소 루트</b>에 있어야 합니다.
<code>git commit --no-verify</code> 로 건너뛸 수 있지만, CI(Step 7)에서 다시 검사합니다.
</div>

---

# 설정 분리 : 왜 필요한가?

| 항목 | 개발 (dev) | 운영 (prod) |
|------|-----------|-------------|
| DEBUG | True | **False** (에러 상세 노출 금지) |
| SECRET_KEY | 기본값 OK | **환경변수 필수** |
| ALLOWED_HOSTS | localhost | 실제 도메인 / IP |
| 정적 파일 | runserver 가 처리 | whitenoise / Nginx |

```
config/settings/
├── __init__.py
├── base.py     # 공통 설정 (앱, 미들웨어, DB, 로깅)
├── dev.py      # 개발용
└── prod.py     # 운영용
```

---

# base.py : 공통 설정

```python
# config/settings/base.py 기준으로 세 단계 위가 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

# SECRET_KEY, DEBUG, ALLOWED_HOSTS 는 환경별 파일(dev.py / prod.py)에서 정의한다

INSTALLED_APPS = [...]
DATABASES = {...}            # PostgreSQL (환경변수)

LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler", ...}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

> 파일이 한 단계 깊어졌으므로 `BASE_DIR` 에 `.parent` 하나 추가!

---

# 🛠 TODO 1~2 : dev.py

```python
"""개발 환경 설정."""

import os

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-key")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
```

- `# noqa: F403` : "star import 경고를 이 줄에서는 무시" (설정 파일에서는 관례)

---

# 🛠 TODO 3~4 : prod.py

```python
"""운영 환경 설정: 모든 비밀값은 반드시 환경변수로 주입한다."""

import os

from .base import *  # noqa: F403


def env_list(name):
    """'a,b,c' 형태의 환경변수를 리스트로 변환한다."""
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


DEBUG = False

# 값이 없으면 KeyError 로 즉시 실패 → 잘못된 설정으로 운영되는 것을 막는다
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
```

---

# 어떤 설정을 쓸지 지정하기

| 실행 방법 | 설정 모듈 | 지정 위치 |
|-----------|-----------|-----------|
| `python manage.py ...` | `config.settings.dev` | `manage.py` 기본값 |
| `pytest` | `config.settings.dev` | `pytest.ini` |
| gunicorn (운영) | `config.settings.prod` | `wsgi.py` 기본값 / 환경변수 |

```python
# manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
```

```bash
# 운영 설정으로 점검해 보기
DJANGO_SETTINGS_MODULE=config.settings.prod DJANGO_SECRET_KEY=x \
  python manage.py check --deploy
```

---

# ✅ 체크포인트

- [ ] `ruff check .` → **All checks passed!**
- [ ] `ruff format --check .` → 변경 없음
- [ ] `pre-commit install` 후 커밋 시 훅 실행 확인
- [ ] `config/settings/` 3개 파일로 분리, `pytest` → **26 passed**
- [ ] prod 설정에서 `DJANGO_SECRET_KEY` 가 없으면 실패함을 확인

---

# 정리

- **ruff** : 린트 + 포맷을 하나의 빠른 도구로
- **pre-commit** : 품질 검사를 커밋 단계에서 강제
- **settings 분리** : 개발은 편하게, 운영은 안전하게
- **requirements 분리** : 운영 이미지는 필요한 것만

### 다음 시간 ▶ Step 6. Docker 컨테이너화
