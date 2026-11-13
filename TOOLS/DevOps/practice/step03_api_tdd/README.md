# Step 3. DRF API TDD

- 슬라이드: `slides/03_api_tdd.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `todos/serializers.py` TODO 1
2. `todos/views.py` TODO 2~3 (CRUD + `?is_done` 필터)
3. `todos/urls.py` TODO 4 (Router 등록)

## 주요 명령

```bash
pytest -v
pytest --cov=todos --cov-report=term-missing
python manage.py runserver   # http://127.0.0.1:8000/api/todos/
```
