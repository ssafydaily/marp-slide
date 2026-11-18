# Step 1. 개발 환경 구성

- 슬라이드: `slides/01_setup.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `config/settings.py` TODO 1: PostgreSQL `DATABASES` 설정
2. `config/views.py` TODO 2: `/health/` 뷰 구현
3. `config/urls.py` TODO 3: URL 연결

## 주요 명령

```bash
docker compose -f compose.db.yml up -d
python manage.py migrate
pytest
```
