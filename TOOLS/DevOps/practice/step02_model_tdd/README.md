# Step 2. TDD & 모델

- 슬라이드: `slides/02_tdd_basics.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `pytest` 실행 → 실패(Red) 확인
2. `config/settings.py` TODO 1: `todos` 앱 등록
3. `todos/models.py` TODO 2~3: `Todo` 모델 + 마이그레이션
4. `pytest` 통과(Green) → 리팩터링

## 주요 명령

```bash
python manage.py makemigrations todos
python manage.py migrate
pytest -v
```
