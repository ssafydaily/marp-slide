---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    font-size: 2 rem;
    position: absolute;
    left: 50px;
    top: 50px;
  }
  h2 {
    font-size: 1.5 rem;
  }
  h3 {
    font-size: 1 rem;
  }
---

## 파이썬 Type Hint의 장점

### 개요

- 파이썬은 동적 타입 언어라 타입을 명시하지 않아도 실행되지만, 3.5버전부터 도입된 type hint를 활용하면 개발 경험과 코드 품질이 크게 향상됩니다. 

- 중요한 전제는 **type hint는 기본적으로 런타임에 강제되지 않는다**는 점입니다. 파이썬 인터프리터는 이를 무시하고 실행합니다.

-------------------

## 🛠️ 개발 시 (Static Analysis)

- type hint의 진짜 효과는 대부분 개발 단계에서 발휘됩니다.

### 1. 정적 타입 검사 (mypy, pyright, pytype)

```python
def greet(name: str) -> str:
    return "Hello, " + name

greet(123)  # mypy: error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

실행 전에 타입 오류를 잡아낼 수 있습니다. CI/CD 파이프라인에 `mypy`를 붙이면 타입 오류가 있는 코드가 배포되는 것을 막을 수 있습니다.

----------------

### 2. IDE 자동완성 및 인텔리센스

```python
def get_user(user_id: int) -> dict[str, str]:
    return {"name": "Alice", "email": "alice@example.com"}

user = get_user(1)
user["name"].  # IDE가 str의 메서드 목록을 자동완성으로 제시
```

반환 타입을 알기 때문에 IDE(VS Code, PyCharm 등)가 정확한 자동완성을 제공합니다. 타입 없이는 IDE가 `user["name"]`이 `str`인지 `int`인지 알 수 없습니다.

----------------

### 3. 코드 문서화 효과

```python
# ❌ 타입 힌트 없음 — 인자가 뭔지, 반환값이 뭔지 불분명
def process(data, config, verbose):
    ...

# ✅ 타입 힌트 있음 — 시그니처만 봐도 사용법이 명확
def process(
    data: list[dict[str, Any]],
    config: ProcessConfig,
    verbose: bool = False,
) -> ProcessResult:
    ...
```

docstring 없이도 함수의 의도와 사용법이 명확해집니다.

----------------

### 4. 리팩토링 안전성

타입 정보가 있으면 IDE가 심볼 추적, 안전한 rename, 사용처 검색을 훨씬 정확하게 합니다. 타입 없이는 동적 특성 때문에 IDE가 "아마도 이 변수일 것"이라고 추측만 합니다.

----------------

## ⚙️ 실행 시 (Runtime)

### 기본 동작: 힌트는 무시됨

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", " world")  # 정상 실행됨! → "hello world"
```

- 인터프리터는 type hint를 **완전히 무시**하고 실행합니다. 
- 잘못된 타입을 넘겨도 오류가 발생하지 않습니다.

----------------

### 런타임에서 접근 가능한 메타데이터

- type hint는 `__annotations__` 속성에 저장되어 런타임에 읽을 수 있습니다.

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet.__annotations__)
# {'name': <class 'str'>, 'return': <class 'str'>}
```

이를 활용하면 다음과 같은 고급 기법이 가능합니다.

----------------

### 1. `typing.get_type_hints()` — 지연 평가 힌트 처리

```python
from typing import get_type_hints

class User:
    name: str
    age: int

print(get_type_hints(User))
# {'name': <class 'str'>, 'age': <class 'int'>}
```

----------------

### 2. 런타임 타입 검증 — Pydantic

Pydantic은 type hint를 읽어 런타임에 실제 검증을 수행하는 대표적인 라이브러리입니다.

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

User(name="Alice", age="not_a_number")
# ValidationError: age: value is not a valid integer
```

FastAPI가 Pydantic을 기반으로 요청/응답을 자동 검증하는 것도 이 메커니즘을 활용합니다.

----------------

### 3. 데코레이터를 통한 런타임 강제

직접 type hint를 읽어 런타임 검증 데코레이터를 만들 수도 있습니다.

```python
import functools, inspect

def enforce_types(func):
    hints = func.__annotations__
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for param, value in zip(inspect.signature(func).parameters, args):
            expected = hints.get(param)
            if expected and not isinstance(value, expected):
                raise TypeError(f"{param}: expected {expected}, got {type(value)}")
        return func(*args, **kwargs)
    return wrapper

@enforce_types
def add(a: int, b: int) -> int:
    return a + b

add("hi", 1)  # TypeError: a: expected <class 'int'>, got <class 'str'>
```
----------------

### 4. `dataclasses` 및 표준 라이브러리의 활용

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)  # __init__ 자동 생성에 type hint가 활용됨
```

`dataclass`는 `__annotations__`를 읽어 `__init__`, `__repr__`, `__eq__` 등을 자동 생성합니다.

----------------

<style scoped>
table { font-size: 24px}
</style>

## 정리

| 구분 | 적용 시점 | 도구 / 방식 | 효과 |
|---|---|---|---|
| 정적 검사 | 개발 / CI | mypy, pyright | 실행 전 타입 오류 감지 |
| IDE 지원 | 개발 | VS Code, PyCharm | 자동완성, 오류 표시 |
| 문서화 | 개발 | 코드 리뷰, 읽기 | 가독성, 유지보수성 향상 |
| 런타임 무시 | 실행 | 파이썬 인터프리터 | 힌트는 실행에 영향 없음 |
| 런타임 검증 | 실행 | Pydantic, 커스텀 데코레이터 | 실제 타입 강제 가능 |
| 메타프로그래밍 | 실행 | dataclass, FastAPI 등 | `__annotations__` 활용 |

<br>

- `type hint` 는 **파이썬에 타입 시스템을 추가하는 것이 아니라, 도구와 라이브러리가 활용할 수 있는 메타데이터를 코드에 붙이는 것** 이라고 이해하면 가장 정확.