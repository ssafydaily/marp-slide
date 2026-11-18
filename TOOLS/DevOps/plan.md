# DevOps 학습 자료 작업 계획

> 기준 문서: `guide.md`
> 작성일: 2026-11-13

## 1. 목표

- DevOps 개념(문화·프로세스·도구)을 이해하고, **DRF(Django REST Framework) 프로젝트**를 예시로
  "코드 작성 → 테스트 → 버전관리 → 컨테이너화 → CI/CD → 운영" 전체 흐름을 직접 실습한다.
- 모든 기능 개발은 **pytest 기반 TDD(Red → Green → Refactor)** 로 진행한다.
- 단계별로 **템플릿 코드(빈칸/TODO)** 와 **완성 코드**를 분리 제공한다.
- 실습 가이드는 **Marp 슬라이드(`theme: dark-plus-code`)** 형식의 마크다운으로 작성한다.

> 확정 사항: DFR = DRF 오타 / 예시 도메인 = Todo API / CD = 실제 서버(EC2) 배포까지 / DB = PostgreSQL

## 2. 실습 환경

| 항목 | 버전/도구 |
|------|-----------|
| Python | 3.11 |
| Web | Django 5.2 (LTS), djangorestframework 3.16 |
| DB | PostgreSQL 16 (Docker 컨테이너로 실행), 드라이버 `psycopg[binary]` 3 |
| Test | pytest, pytest-django, pytest-cov |
| 품질 | ruff (lint/format), pre-commit |
| VCS | Git, GitHub (PR, Branch protection) |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions, GHCR(GitHub Container Registry) |
| 배포 서버 | AWS EC2(Ubuntu) + Docker Compose |
| Web Server | Nginx(리버스 프록시) + gunicorn (+ whitenoise 정적파일) |
| 배포 방식 | GitHub Actions → SSH 접속 → 이미지 pull & 재기동 |

## 3. 예시 프로젝트: `todo_api`

- `Todo` 모델: `title`, `description`, `is_done`, `created_at`, `updated_at`
- API: `GET/POST /api/todos/`, `GET/PUT/PATCH/DELETE /api/todos/{id}/`
- 부가: 완료 여부 필터(`?is_done=true`), 제목 검색(`?search=`), 헬스체크 `GET /health/`(DB 연결 포함)

## 4. 디렉터리 구조

```
TOOLS/DevOps/
├── guide.md / plan.md
├── slides/                       # Marp 슬라이드 (dark-plus-code)
│   ├── 00_devops_intro.md ... 09_operate_wrapup.md
└── practice/
    ├── step01_setup/{template,solution}
    ├── step02_model_tdd/{template,solution}
    ├── step03_api_tdd/{template,solution}
    ├── step04_git/{template,solution}
    ├── step05_quality/{template,solution}
    ├── step06_docker/{template,solution}
    ├── step07_ci/{template,solution}
    └── step08_cd/{template,solution}    # deploy/ (compose.prod, nginx, deploy.sh, rollback.sh)
```

- 각 step 폴더는 **그 자체로 실행 가능한 완전한 프로젝트** (복사해서 GitHub 저장소 루트로 사용)
- 각 step의 `solution/`은 다음 step `template/`의 출발점

## 5. 단계별 학습 계획

| Step | 슬라이드 | 주제 | 주요 내용 |
|------|----------|------|-----------|
| 0 | `00_devops_intro.md` | DevOps 개념 | 정의, 등장 배경, CALMS, DevOps 무한 루프, CI/CD, 실습 로드맵 |
| 1 | `01_setup.md` | 개발 환경 구성 | venv, Django/DRF 프로젝트, PostgreSQL 컨테이너(`compose.db.yml`), `.env`, pytest 설정, `/health/` 첫 테스트 |
| 2 | `02_tdd_basics.md` | TDD & pytest 기초 | TDD 사이클, assert/fixture/parametrize/mark, `django_db`, Todo 모델 TDD |
| 3 | `03_api_tdd.md` | DRF API TDD | Serializer, ViewSet/Router, `APIClient` fixture, CRUD·필터·검증 테스트, 커버리지 |
| 4 | `04_git_github.md` | Git & GitHub 협업 | GitHub Flow, 커밋 컨벤션, PR/Issue 템플릿, Branch protection, 검색 기능 PR 실습 |
| 5 | `05_code_quality.md` | 코드 품질 자동화 | ruff, pre-commit, settings 분리(base/dev/prod), requirements 분리 |
| 6 | `06_docker.md` | Docker 컨테이너화 | 멀티스테이지 Dockerfile, gunicorn, whitenoise, compose(db+web+test), healthcheck, DB 대기 스크립트 |
| 7 | `07_ci.md` | CI – GitHub Actions | lint → test(PostgreSQL service container) → docker build, 캐시, 상태체크 |
| 8-1 | `08-1_server_setup.md` | 배포 서버 준비 | EC2 생성, 보안그룹, Docker 설치, Nginx, 서버 `.env` 준비 |
| 8-2 | `08-2_cd.md` | CD – 자동 배포 | GHCR push(`latest`+SHA), Secrets, SSH 배포, 배포 후 헬스체크 |
| 9 | `09_operate_wrapup.md` | 운영 & 마무리 | 로그, 모니터링, 롤백(`rollback.sh`), DB 백업, 회고, 확장 과제 |

## 6. 템플릿 / 완성 코드 작성 원칙

- **template**: 테스트는 먼저 제공(Red 체험), 구현부는 `# TODO` + `raise NotImplementedError` 등 → `pytest` 실패가 정상
- **solution**: `pytest` 전체 통과, `ruff check` 통과(step05 이후)

## 7. 슬라이드 작성 규칙

- front matter: `marp: true`, `theme: dark-plus-code`, `paginate: true`
- 구성: 학습 목표 → 개념 → 코드/명령 예시 → 실습 지시 → 체크포인트 → 정리
- callout(`tip/info/warning`), `cols` 레이아웃 활용, 다이어그램은 텍스트 도식
- 첫 페이지(`<!-- _class: lead -->`) 가독성: 각 파일 front matter 의 `style:` 에서 `section.lead h1/h2/p` 를 밝은 색으로 지정
  (공용 테마 `dark-plus-code.css` 의 `h1` 색 `#0c2a42` 가 어두운 lead 배경에서 안 보이기 때문. 공용 테마는 다른 덱도 쓰므로 수정하지 않음)
- 빌드 (`slides/` 폴더에서, `--theme-set` 은 배열 옵션이라 **맨 뒤**에 둘 것):
  `marp 01_setup.md -o out/01_setup.html --theme-set ../../../dark-plus-code.css`

## 8. 작업 순서 (진행 체크리스트)

- [x] 1. 디렉터리 골격 생성
- [x] 2. Step 0 ~ 9 슬라이드 작성
- [x] 3. Step 1 ~ 8 template / solution 작성
- [x] 4-a. 검증: 각 solution `pytest` 통과(SQLite 대체 실행), step05~08 `ruff` 통과, YAML/셸 문법 검사
- [x] 4-b. 검증: Docker + PostgreSQL 환경에서 `pytest`, `docker compose up` 실제 동작
- [x] 4-c. 검증: 운영 compose(Nginx+web+db) + `deploy.sh`/`rollback.sh` 로컬 레지스트리로 배포 시뮬레이션, `pg_dump` 백업/복원
- [x] 5. 검증: Marp 렌더링 확인 (11개 덱, dark-plus-code 테마 적용)
- [ ] 6. 검증: EC2 실제 배포 동작 확인 (push → 자동 배포 → `/health/` 응답)

## 9. 확인이 필요한 사항

1. 수업 시간(총 차시) 기준 분량 조정 필요 여부
2. 저장소의 다른 슬라이드 덱에도 첫 페이지 색상 문제가 있음 → 공용 테마(`dark-plus-code.css` 의 `section.lead h1`)를 고칠지 여부

## 10. DB 운용 원칙 (PostgreSQL, 실습 예외 최소화)

| 위험 요소 | 대응 |
|-----------|------|
| PostgreSQL 설치 실패/버전 차이 | 로컬 설치 없이 **Docker 공식 이미지 `postgres:16-alpine`** 만 사용 |
| 접속 정보 불일치 | 모든 설정을 **환경변수 + 동일 기본값**(`todo_db / todo_user / todo_password`)으로 통일, `.env.example` 제공 |
| 5432 포트 충돌(로컬 PostgreSQL 존재) | 호스트 포트를 `POSTGRES_PORT` 로 변경 가능(예: 5433), 컨테이너 내부 통신은 항상 5432 |
| DB 기동 전 앱 접속 → 연결 오류 | compose `healthcheck` + `depends_on: condition: service_healthy`, 엔트리포인트의 `wait_for_db.py` 재시도 |
| 테이블 없음 오류 | 컨테이너 시작 시 `migrate --noinput` 자동 실행 |
| 테스트 DB 생성 권한 | 공식 이미지의 `POSTGRES_USER`는 superuser → pytest-django 테스트 DB 자동 생성 가능 |
| Windows 드라이버 빌드 오류 | `psycopg[binary]` 사용(컴파일 불필요) |
| 데이터 초기화 필요 | `docker compose down -v` 로 볼륨까지 리셋하는 방법 안내 |
| 운영 DB 노출 | 운영 compose에서 DB 포트 미공개(`ports` 없음), 백업 명령(`pg_dump`) 안내 |

## 11. 작업 이력 & 주요 결정 (2026-11-13)

| 결정 / 변경 | 이유 |
|-------------|------|
| DB: SQLite 검토 → **PostgreSQL 로 확정** | 사용자 요청. 대신 §10 의 예외 방지 장치를 모두 적용 |
| 모든 compose 파일에 `name: todo-api` | Step 이 바뀌어도 같은 DB 볼륨(`todo-api_pgdata`)을 공유 → 실습 중 데이터/접속 혼란 방지 |
| Step 6 부터 `compose.db.yml` 제거 | `docker-compose.yml` 의 db 서비스로 대체 (슬라이드에서 기존 DB `down` 안내) |
| Dockerfile 3단계(builder/runtime/test) | 운영 이미지에 pytest 미포함, 테스트는 runtime 위에서 동일 환경으로 실행 |
| 정적 파일은 whitenoise | Nginx 에 정적 파일 볼륨 공유가 필요 없어 운영 구성 단순화 |
| `entrypoint.sh` CRLF 제거(`sed`) + `.gitattributes` | Windows 에서 작성한 셸 스크립트의 `no such file or directory` 오류 방지 |
| `TOOLS/DevOps/.gitignore` 에 `!scripts/` | 루트 `.gitignore` 의 `[Ss]cripts`(가상환경용) 규칙 때문에 `scripts/wait_for_db.py` 가 커밋에서 빠지던 문제 |
| `deploy.sh`: **pull 성공 후에만 `.env` 갱신** | 검증 중 없는 태그로 배포 시 `.env` 의 `IMAGE_TAG` 가 오염되는 버그 발견 → 수정 |
| `.env.prod.example` 에서 `IMAGE_TAG=latest` 제거 | 첫 배포 시 `PREVIOUS_IMAGE_TAG=latest` 가 기록되어 롤백 대상이 부적절했음 |
| 백업 명령 `pg_dump --clean --if-exists` | 기존 테이블이 있는 DB 에 복원 시 충돌 → 덮어쓰기 복원 가능하도록 |
| 첫 페이지 색상은 각 슬라이드 front matter 에서 지정 | 공용 테마 수정 시 다른 덱에 영향 |

### 검증 방법 (재현용)

- **SQLite 대체 실행**: 임시 settings(`from config.settings[.dev] import *` + `DATABASES` 를 sqlite `:memory:`)로 `pytest --ds=<모듈>`
- **PostgreSQL 실제 실행**: `docker compose -f compose.db.yml up -d` → `migrate` → `pytest` (Step 1~5), Step 6 `docker compose up -d --build` + `--profile test run --rm test`
- **배포 시뮬레이션**: `registry:2` 를 `localhost:5000` 으로 띄워 GHCR 대신 사용,
  `COMPOSE_PROJECT_NAME=todo-api-sim` 으로 개발 볼륨과 분리한 뒤 `deploy.sh`(v1→v2→없는 태그)·`rollback.sh`·`pg_dump` 복원 확인
- **슬라이드**: `npm install @marp-team/marp-cli@4` 후 HTML/PNG 렌더링으로 테마 적용·넘침 확인

## 12. 다음 할 일

- [ ] GitHub 저장소에서 CI(`ci.yml`) / CD(`cd.yml`) 실제 실행 확인 (step 폴더를 별도 저장소 루트로 복사해서)
- [ ] EC2 실제 배포 (Secrets 3개 등록 → merge → `/health/` 확인 → 롤백 실습)
- [ ] §9 확인 사항 결정 (차시별 분량, 공용 테마 수정 여부)
- [ ] (선택) `config/views.py` 503 경로 테스트를 solution 에 추가할지 결정 (현재는 Step 3 슬라이드의 도전 과제)

## 13. 다른 PC 에서 이어서 작업하기

```bash
git pull
cd TOOLS/DevOps
claude          # Claude Code 실행 후: "plan.md 를 읽고 현재 작업 상태를 파악해줘"
```

- 로컬 실행 환경(가상환경, Docker 이미지/볼륨, Marp CLI)은 저장소에 없으므로 `practice/README.md` 절차로 다시 구성
