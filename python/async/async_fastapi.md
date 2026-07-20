---
marp: true
theme: dark-plus-code
paginate: true
style: |
  
---

# 소개
- 3rd-party 라이브리러 사용시 `await`를 사용해 호출해야 하는 경우:
```python
results = await some_library()
```

### 예시

- **FastAPI** 의 경로 처리 함수를 `async def` 를 사용해 선언:

```python
@app.get('/')
async def read_results():
    results = await some_library()
    return results
```

> 참고
> - `async def` 로 작성된 함수 내부에서만 `await` 를 사용할 수 있다.

--------------








