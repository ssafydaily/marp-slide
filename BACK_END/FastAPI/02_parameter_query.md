---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    font-size: 1.5rem;
    position: absolute;
    left: 50px;
    top: 50px;
  }
  h2 {
    font-size: 1.3rem;
  }
  h3 {
    font-size: 1rem;
  }
---

# 쿼리 매개 변수

- 경로 매개변수에 포함되지 않는 다른 함수 매개변수를 선언하면 **쿼리 매개변수**로 간주된다.

```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

---------------------

# 선택적 매개 변수

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

--------------------

# 필수 쿼리 매개변수

- 경로가 아닌 매개변수에 대한 기본값을 선언하면, 해당 매개변수는 필수(Required)가 아님.
- 특정값을 추가하지 않고 선택적으로 만들기 위해선 기본값을 None으로 설정
- **기본값을 선언하지 않으면 필수** 가 된다.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item
```

----------------------

