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

# Pydantic

- **Pydantic** 은 데이터 검증을 수행하는 파이썬 라이브러리

- 속성을 가진 클래스 형태로 데이터의 "모양(shape)"을 선언

  - 각 속성은 타입을 가진다.

- 클래스의 인스턴스를 몇 가지 값으로 생성하면, 값들을 검증하고, (그런 경우라면) 적절한 타입으로 변환한 뒤, 모든 데이터를 가진 객체를 제공

> [pydantic 알아보기](https://pydantic.dev/docs/)
------------

# 어노테이션이 있는 타입 힌트

- `Annotated` 를 사용해 타입 힌트에 추가 메타데이터를 넣을 수 있다.
- `Annotated` 는 `typing` 에서 `import`

```python
from typing import Annotated


def say_hello(name: Annotated[str, "this is just metadata"]) -> str:
    return f"Hello {name}"
```

- 파이썬 자체는 `Annotated` 로 아무것도 하지 않음. 
- 애플리케이션이 어떻게 동작하길 원하는지에 대한 추가 메타데이터를 **FastAPI** 에 제공할 수 있다.

- `Annotated`에 전달하는 첫 번째 타입 매개변수가 실제 타입이고, 나머지는 다른 도구를 위한 메타데이터일 뿐이다.

