# Step 6. Docker 컨테이너화

- 슬라이드: `slides/06_docker.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `config/settings/prod.py` TODO 9: whitenoise
2. `Dockerfile` TODO 1~5
3. `.dockerignore` TODO 6
4. `docker-compose.yml` TODO 7~8 (web, test 서비스)

## 주요 명령

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health/
docker compose --profile test run --rm test
docker compose logs -f web
```
