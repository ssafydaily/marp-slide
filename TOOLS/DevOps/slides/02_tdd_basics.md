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

# Step 2. TDD & pytest 기초

## 테스트로 Todo 모델 만들기

---

# 학습 목표

- TDD 사이클(Red → Green → Refactor)을 직접 경험한다
- pytest 의 핵심 문법(assert, fixture, parametrize, mark)을 익힌다
- `@pytest.mark.django_db` 로 DB 를 사용하는 테스트를 작성한다
- 테스트를 먼저 보고 **Todo 모델**을 구현한다

📁 실습 폴더: `practice/step02_model_tdd/template`

---

# TDD 사이클

```
        ┌────────────────────────────────────┐
        ▼                                    │
  🔴 Red ──────────▶ 🟢 Green ──────────▶ 🔵 Refactor
  실패하는 테스트      통과하는 최소 코드       중복 제거 · 개선
  작성                                     (테스트는 계속 통과)
```

| 단계 | 질문 |
|------|------|
| Red | "무엇을 만들어야 하지?" → 테스트로 **요구사항을 표현** |
| Green | "가장 간단하게 통과시키려면?" |
| Refactor | "더 읽기 좋게 만들 수 있나?" |

---

# 왜 TDD 인가?

- 테스트가 곧 **실행 가능한 명세서**
- 코드를 바꿔도 **안전망**이 있다 → 리팩터링에 대한 두려움 ↓
- CI 에서 자동 실행 → **배포 전에 버그 차단**
- 테스트하기 쉬운 코드 = **설계가 좋은 코드**

<div class="callout tip">
<div class="callout-title">현실적인 TDD</div>
모든 코드를 100% TDD 로 짤 필요는 없습니다. 핵심 로직과 API 동작부터 테스트로 고정하세요.
</div>

---

# pytest 기초 1 : assert

```python
def add(a, b):
    return a + b


def test_add():
    assert add(1, 2) == 3
```

- 함수 이름이 `test_` 로 시작하면 테스트
- 그냥 **`assert`** 문 하나로 검증 (unittest 의 `assertEqual` 불필요)
- 실패 시 pytest 가 값을 자세히 보여줌

```text
>       assert add(1, 2) == 4
E       assert 3 == 4
```

---

# pytest 기초 2 : 예외 검증

```python
import pytest


def divide(a, b):
    return a / b


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

- "이 코드는 **예외가 발생해야 한다**" 를 테스트

---

# pytest 기초 3 : fixture

```python
import pytest


@pytest.fixture
def numbers():
    """여러 테스트에서 재사용할 준비 데이터."""
    return [1, 2, 3]


def test_sum(numbers):          # 인자 이름으로 fixture 주입
    assert sum(numbers) == 6


def test_len(numbers):
    assert len(numbers) == 3
```

- 테스트 **준비 코드(Arrange)를 재사용**
- `conftest.py` 에 두면 모든 테스트 파일에서 사용 가능

---

# pytest 기초 4 : parametrize

```python
import pytest


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(1, 2, 3), (0, 0, 0), (-1, 1, 0)],
)
def test_add(a, b, expected):
    assert a + b == expected
```

```text
test_add[1-2-3] PASSED
test_add[0-0-0] PASSED
test_add[-1-1-0] PASSED
```

- 하나의 테스트로 **여러 입력값** 검증

---

# pytest-django 가 제공하는 것

| 기능 | 설명 |
|------|------|
| `@pytest.mark.django_db` | 이 테스트에서 DB 접근 허용 |
| `pytestmark = pytest.mark.django_db` | 파일 전체에 적용 |
| `client` fixture | Django 테스트 HTTP 클라이언트 |
| `db` fixture | fixture 안에서 DB 사용 |
| 테스트 DB | `test_todo_db` 자동 생성, 테스트마다 **롤백** |

<div class="callout info">
<div class="callout-title">테스트 격리</div>
각 테스트는 트랜잭션 안에서 실행되고 끝나면 롤백됩니다. 테스트끼리 데이터가 섞이지 않아요.
</div>

---

# 좋은 테스트의 구조 : AAA

```python
def test_mark_done_changes_is_done():
    # Arrange (준비)
    todo = Todo.objects.create(title="공부하기")

    # Act (실행)
    todo.mark_done()
    todo.refresh_from_db()

    # Assert (검증)
    assert todo.is_done is True
```

- 테스트 이름은 **무엇을 검증하는지** 문장처럼
- 하나의 테스트는 **하나의 동작**만

---

# 실습 : todos 앱 만들기

```bash
python manage.py startapp todos    # (template 에는 이미 생성됨)
```

🛠 **TODO 1** : `config/settings.py` 에 앱 등록

```python
INSTALLED_APPS = [
    ...
    "rest_framework",
    # local apps
    "todos",
]
```

---

# 🔴 Red : 테스트 먼저 읽기

`tests/test_models.py` (제공됨)

```python
pytestmark = pytest.mark.django_db


def test_create_todo_with_defaults():
    todo = Todo.objects.create(title="장보기")

    assert todo.title == "장보기"
    assert todo.description == ""
    assert todo.is_done is False
    assert todo.created_at is not None


def test_str_returns_title():
    assert str(Todo(title="운동하기")) == "운동하기"
```

---

# 테스트가 말해주는 요구사항

```python
def test_latest_todo_comes_first():
    first = Todo.objects.create(title="첫 번째")
    second = Todo.objects.create(title="두 번째")
    assert list(Todo.objects.all()) == [second, first]


@pytest.mark.parametrize("title", ["a", "가" * 200])
def test_title_within_max_length_is_valid(title):
    Todo(title=title).full_clean()


def test_title_over_max_length_is_invalid():
    with pytest.raises(ValidationError):
        Todo(title="가" * 201).full_clean()
```

> 최신순 정렬 · 제목 최대 200자 · `mark_done()` 메서드

---

# 🔴 실행해서 실패 확인

```bash
pytest
```

```text
E   ImportError: cannot import name 'Todo' from 'todos.models'
=========================== 1 error in 0.20s ===========================
```

- 아직 `Todo` 모델이 없으니 실패가 정상
- 에러 메시지가 **다음에 할 일**을 알려줌

---

# 🛠 TODO 2 : Todo 모델 (Green)

`todos/models.py`

```python
from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title
```

---

# mark_done 메서드

```python
    def mark_done(self):
        """할 일을 완료 상태로 변경한다."""
        self.is_done = True
        self.save(update_fields=["is_done", "updated_at"])
```

- `update_fields` : 바뀐 컬럼만 UPDATE → 효율적

<div class="callout warning">
<div class="callout-title">왜 ordering 에 "-id" 도?</div>
같은 시각(밀리초 단위)에 생성되면 <code>created_at</code> 이 같을 수 있습니다.
보조 기준을 두어 <b>테스트가 가끔 실패하는(flaky) 문제</b>를 막습니다.
</div>

---

# 🛠 TODO 3 : 마이그레이션

```bash
python manage.py makemigrations todos
python manage.py migrate
```

```text
Migrations for 'todos':
  todos/migrations/0001_initial.py
    + Create model Todo
```

- 마이그레이션 파일도 **코드처럼 커밋**한다
- 운영 서버에서는 같은 파일로 테이블이 만들어짐

---

# 🟢 Green

```bash
pytest -v
```

```text
tests/test_health.py::test_health_returns_ok PASSED
tests/test_models.py::test_create_todo_with_defaults PASSED
tests/test_models.py::test_str_returns_title PASSED
tests/test_models.py::test_mark_done_changes_is_done PASSED
tests/test_models.py::test_latest_todo_comes_first PASSED
tests/test_models.py::test_title_within_max_length_is_valid[a] PASSED
tests/test_models.py::test_title_within_max_length_is_valid[가가...] PASSED
tests/test_models.py::test_title_over_max_length_is_invalid PASSED
============================ 8 passed ============================
```

---

# 🔵 Refactor & 관리자 등록 (선택)

`todos/admin.py`

```python
from django.contrib import admin

from todos.models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "is_done", "created_at"]
    list_filter = ["is_done"]
    search_fields = ["title"]
```

```bash
python manage.py createsuperuser
pytest          # 리팩터링 후에도 여전히 통과하는지 확인!
```

---

# 유용한 pytest 옵션

| 명령 | 설명 |
|------|------|
| `pytest -v` | 테스트 이름 자세히 |
| `pytest -x` | 첫 실패에서 중단 |
| `pytest -k mark_done` | 이름에 `mark_done` 포함된 테스트만 |
| `pytest tests/test_models.py` | 특정 파일만 |
| `pytest --lf` | 지난번 실패한 테스트만 |
| `pytest --create-db` | 테스트 DB 강제 재생성 |

---

# ✅ 체크포인트

- [ ] 테스트를 먼저 실행해 **실패(Red)** 를 확인했다
- [ ] `Todo` 모델 구현 후 **8 passed**
- [ ] `todos/migrations/0001_initial.py` 생성됨
- [ ] fixture / parametrize / django_db 의 역할을 설명할 수 있다

---

# 정리

- TDD : **테스트로 요구사항을 먼저 표현**하고 코드로 통과시킨다
- pytest : `assert`, `fixture`, `parametrize`, `mark`
- pytest-django : 테스트 전용 DB + 테스트마다 롤백 → **격리**
- 마이그레이션 파일도 버전관리 대상

### 다음 시간 ▶ Step 3. DRF API TDD
