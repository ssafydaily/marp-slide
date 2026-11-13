# DevOps 실습 코드 (todo-api)

| Step | 폴더 | 슬라이드 | 핵심 |
|------|------|----------|------|
| 1 | `step01_setup` | `slides/01_setup.md` | Django/DRF + PostgreSQL 컨테이너 + `/health/` |
| 2 | `step02_model_tdd` | `slides/02_tdd_basics.md` | Todo 모델 TDD |
| 3 | `step03_api_tdd` | `slides/03_api_tdd.md` | DRF API TDD |
| 4 | `step04_git` | `slides/04_git_github.md` | GitHub Flow, PR/Issue 템플릿, 검색 기능 |
| 5 | `step05_quality` | `slides/05_code_quality.md` | ruff, pre-commit, settings 분리 |
| 6 | `step06_docker` | `slides/06_docker.md` | Dockerfile, docker compose |
| 7 | `step07_ci` | `slides/07_ci.md` | GitHub Actions CI |
| 8 | `step08_cd` | `slides/08-1_server_setup.md`, `slides/08-2_cd.md` | EC2 배포, CD |

## 폴더 규칙

- `template/` : 학습자용. `TODO` 를 채워 테스트를 통과시키는 것이 목표
- `solution/` : 완성 코드. 다음 Step 의 `template/` 출발점
- 각 폴더는 **그대로 복사해서 GitHub 저장소 루트로 사용**할 수 있는 독립 프로젝트입니다.

## 공통 실행 방법 (Step 1 ~ 5)

```bash
python -m venv .venv
source .venv/Scripts/activate          # Windows Git Bash  (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt        # Step 5 부터는 requirements-dev.txt
cp .env.example .env
docker compose -f compose.db.yml up -d # PostgreSQL 실행
docker compose -f compose.db.yml ps    # STATUS 가 healthy 인지 확인
python manage.py migrate
pytest
```

## Step 6 이후

```bash
docker compose up -d --build                  # db + web
docker compose --profile test run --rm test   # 컨테이너 안에서 pytest
```

## 자주 만나는 문제

| 증상 | 해결 |
|------|------|
| `connection refused` / `could not connect to server` | `docker compose ... ps` 로 db 가 healthy 인지 확인 |
| `port is already allocated` (5432) | `.env` 의 `POSTGRES_PORT=5433` 으로 변경 후 db 재시작 |
| `password authentication failed` | 비밀번호를 바꾼 뒤 기존 볼륨이 남아있음 → `docker compose ... down -v` 후 재시작 |
| `relation "todos_todo" does not exist` | `python manage.py migrate` 실행 |
| 다른 Step 으로 옮겨도 DB 는 공유됨 | 모든 compose 의 프로젝트 이름이 `todo-api` 로 같음 (의도된 설정) |
