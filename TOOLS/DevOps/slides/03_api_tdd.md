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

# Step 3. DRF API TDD

## 테스트로 REST API 완성하기

---

# 학습 목표

- DRF 의 **Serializer · ViewSet · Router** 구조를 이해한다
- `APIClient` fixture 로 API 테스트를 작성한다
- CRUD, 필터, 검증 실패(400), 없는 리소스(404)를 테스트한다
- **커버리지(coverage)** 로 테스트 범위를 측정한다

📁 실습 폴더: `practice/step03_api_tdd/template`

---

# DRF 요청 처리 흐름

```
HTTP 요청
   │
   ▼
Router (URL → ViewSet 메서드 연결)
   │        /api/todos/        → list / create
   │        /api/todos/{id}/   → retrieve / update / partial_update / destroy
   ▼
ViewSet (queryset, 권한, 필터)
   │
   ▼
Serializer (검증: JSON → 객체 / 변환: 객체 → JSON)
   │
   ▼
Model (PostgreSQL)
```

---

# 테스트 피라미드

```
            /\
           /E2E\          적게: 느리고 깨지기 쉬움
          /──────\
         /  API   \       ← 이번 Step 의 중심
        /──────────\
       /  Unit      \     많이: 빠르고 안정적 (모델, 시리얼라이저)
      /──────────────\
```

- **Unit** : 모델, 시리얼라이저 단독 테스트
- **API(통합)** : URL → View → Serializer → DB 전체 흐름

---

# 공용 fixture : conftest.py

`tests/conftest.py`

```python
import pytest
from rest_framework.test import APIClient

from todos.models import Todo


@pytest.fixture
def api_client():
    """DRF API 요청용 클라이언트."""
    return APIClient()


@pytest.fixture
def todo(db):
    """테스트용 할 일 1개."""
    return Todo.objects.create(title="기존 할 일", description="설명")
```

> `conftest.py` 의 fixture 는 **import 없이** 모든 테스트에서 사용

---

# 🔴 Serializer 테스트

`tests/test_serializers.py`

```python
def test_serializer_valid_data():
    serializer = TodoSerializer(data={"title": "새 할 일"})
    assert serializer.is_valid(), serializer.errors


def test_serializer_requires_title():
    serializer = TodoSerializer(data={"description": "제목 없음"})
    assert not serializer.is_valid()
    assert "title" in serializer.errors


def test_serializer_ignores_read_only_fields():
    serializer = TodoSerializer(data={"title": "할 일", "id": 999})
    assert serializer.is_valid()
    assert "id" not in serializer.validated_data
```

---

# 🛠 TODO 1 : Serializer

`todos/serializers.py`

```python
from rest_framework import serializers

from todos.models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "title", "description", "is_done", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
```

- `read_only_fields` : 클라이언트가 보내도 **무시** (id, 생성 시각 위조 방지)
- 공백 제목(`"   "`)은 DRF 가 기본으로 trim 후 **blank 검증**

---

# 🔴 API 테스트 : 목록 · 생성

`tests/test_api.py`

```python
pytestmark = pytest.mark.django_db
LIST_URL = "/api/todos/"


def test_list_todos(api_client, todo):
    response = api_client.get(LIST_URL)

    assert response.status_code == 200
    assert response.json()[0]["title"] == todo.title


def test_create_todo(api_client):
    response = api_client.post(LIST_URL, {"title": "새 할 일"}, format="json")

    assert response.status_code == 201
    assert response.json()["is_done"] is False
    assert Todo.objects.count() == 1
```

---

# 🔴 API 테스트 : 실패 케이스도 테스트!

```python
def test_create_todo_without_title_returns_400(api_client):
    response = api_client.post(LIST_URL, {}, format="json")

    assert response.status_code == 400
    assert "title" in response.json()


def test_retrieve_missing_todo_returns_404(api_client):
    response = api_client.get(detail_url(999999))

    assert response.status_code == 404
```

<div class="callout tip">
<div class="callout-title">TIP</div>
버그는 대부분 "정상 경로"가 아니라 <b>예외 경로</b>에서 발생합니다. 400 / 404 도 꼭 테스트하세요.
</div>

---

# 🔴 API 테스트 : 수정 · 삭제

```python
def test_partial_update_todo(api_client, todo):
    response = api_client.patch(detail_url(todo.id), {"is_done": True}, format="json")

    assert response.status_code == 200
    todo.refresh_from_db()
    assert todo.is_done is True
    assert todo.title == "기존 할 일"      # 다른 필드는 그대로


def test_delete_todo(api_client, todo):
    response = api_client.delete(detail_url(todo.id))

    assert response.status_code == 204
    assert not Todo.objects.filter(id=todo.id).exists()
```

---

# 🔴 API 테스트 : 필터 (parametrize)

```python
@pytest.mark.parametrize(
    ("query", "expected_titles"),
    [("true", ["완료한 일"]), ("false", ["남은 일"])],
)
def test_filter_by_is_done(api_client, query, expected_titles):
    Todo.objects.create(title="완료한 일", is_done=True)
    Todo.objects.create(title="남은 일", is_done=False)

    response = api_client.get(LIST_URL, {"is_done": query})

    assert [item["title"] for item in response.json()] == expected_titles
```

```bash
pytest     # → 13 failed : 아직 API 가 없음 (Red)
```

---

# 🛠 TODO 2~3 : ViewSet

`todos/views.py`

```python
from rest_framework import viewsets

from todos.models import Todo
from todos.serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        is_done = self.request.query_params.get("is_done")
        if is_done is not None:
            queryset = queryset.filter(is_done=is_done.lower() == "true")
        return queryset
```

---

# ModelViewSet = 6개 API 를 한 번에

| 메서드 | URL | ViewSet 액션 | 상태 코드 |
|--------|-----|--------------|-----------|
| GET | `/api/todos/` | `list` | 200 |
| POST | `/api/todos/` | `create` | 201 |
| GET | `/api/todos/{id}/` | `retrieve` | 200 / 404 |
| PUT | `/api/todos/{id}/` | `update` | 200 / 400 |
| PATCH | `/api/todos/{id}/` | `partial_update` | 200 |
| DELETE | `/api/todos/{id}/` | `destroy` | 204 |

---

# 🛠 TODO 4 : Router 등록

`todos/urls.py`

```python
from rest_framework.routers import DefaultRouter

from todos.views import TodoViewSet

router = DefaultRouter()
router.register("todos", TodoViewSet, basename="todo")

urlpatterns = router.urls
```

`config/urls.py` (제공됨)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("api/", include("todos.urls")),
]
```

---

# 🟢 Green

```bash
pytest -v
```

```text
tests/test_api.py::test_list_todos PASSED
tests/test_api.py::test_create_todo PASSED
tests/test_api.py::test_create_todo_without_title_returns_400 PASSED
...
tests/test_serializers.py::test_serializer_ignores_read_only_fields PASSED
============================ 22 passed ============================
```

```bash
python manage.py runserver
# http://127.0.0.1:8000/api/todos/  → DRF Browsable API 로 직접 확인
```

---

# 커버리지 측정

```bash
pytest --cov=todos --cov=config --cov-report=term-missing
```

```text
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
todos/models.py           14      0   100%
todos/serializers.py       7      0   100%
todos/views.py            11      0   100%
config/views.py            9      2    78%   10-11
----------------------------------------------------
TOTAL                     ...            9x%
```

- `Missing` : **테스트가 실행하지 않은 줄**
- `--cov-report=html` → `htmlcov/index.html` 에서 시각적으로 확인

---

# 커버리지 해석 주의

- 커버리지 100% ≠ 버그 0개
- **실행됐는지**만 측정, **올바른지**는 assert 가 검증
- 목표: 숫자보다 **중요한 경로(정상 + 예외)** 를 빠짐없이

<div class="callout info">
<div class="callout-title">도전 과제</div>
<code>config/views.py</code> 의 DB 오류(503) 경로는 테스트되지 않았습니다.
<code>unittest.mock.patch</code> 로 <code>connection.cursor</code> 가 <code>DatabaseError</code> 를 던지도록 만들어 테스트해 보세요.
</div>

---

# ✅ 체크포인트

- [ ] Serializer / ViewSet / Router 의 역할을 설명할 수 있다
- [ ] `pytest` → **22 passed**
- [ ] 400, 404 같은 실패 경로를 테스트했다
- [ ] 커버리지 리포트에서 `Missing` 을 확인했다
- [ ] Browsable API 로 직접 CRUD 해 보았다

---

# 정리

- DRF 구조 : **Router → ViewSet → Serializer → Model**
- `conftest.py` fixture 로 테스트 준비 코드 재사용
- 정상 경로 + **예외 경로(400 / 404)** 모두 테스트
- 커버리지로 테스트 빈틈을 찾되, 숫자에 집착하지 않기

### 다음 시간 ▶ Step 4. Git & GitHub 협업
