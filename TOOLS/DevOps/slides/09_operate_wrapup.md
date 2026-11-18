---
marp: true
theme: dark-plus-code
paginate: true
style: |
  /* 첫 페이지(lead): 어두운 배경에서 잘 보이도록 밝은 글자색 */
  section.lead h1 {
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  section.lead h2 {
    color: #e3f2fd;
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.3);
    opacity: 1;
  }
  section.lead p {
    color: #cbd5e1;
    opacity: 1;
  }
---

<!-- _class: lead -->

# Step 9. 운영 & 마무리

## Operate · Monitor · Feedback

---

# 학습 목표

- 운영 중인 서비스의 **로그**와 **상태**를 확인한다
- 장애 시 **롤백**으로 빠르게 복구한다
- PostgreSQL 데이터를 **백업 / 복원**한다
- 전체 DevOps 파이프라인을 회고하고 **다음 단계**를 계획한다

📁 실습 위치: EC2 서버 `~/todo-api/`

---

# DevOps 루프의 마지막 : Operate & Monitor

```
   Plan → Code → Build → Test → Release → Deploy → [Operate → Monitor]
     ↑                                                        │
     └─────────────────────── Feedback ───────────────────────┘
```

- 배포는 끝이 아니라 **시작**
- 운영에서 얻은 정보(에러, 느린 API, 사용 패턴) → 다음 **Plan** 의 입력

---

# 1) 서비스 상태 확인

```bash
ssh -i deploy_key ubuntu@<EC2_IP>
cd ~/todo-api
alias dc="docker compose -f docker-compose.prod.yml"   # 편의용 별칭

dc ps
```

```text
NAME               SERVICE   STATUS                   PORTS
todo-api-db-1      db        Up 2 hours (healthy)
todo-api-web-1     web       Up 15 minutes (healthy)  8000/tcp
todo-api-nginx-1   nginx     Up 15 minutes            0.0.0.0:80->80/tcp
```

```bash
docker stats --no-stream           # CPU / 메모리 사용량
df -h                              # 디스크 사용량
```

---

# 2) 로그 보기

```bash
dc logs --tail=100 web             # 최근 100줄
dc logs -f web                     # 실시간 (Ctrl+C 종료)
dc logs --since=30m nginx          # 최근 30분
dc logs web | grep -E "ERROR|Traceback"
```

| 서비스 | 로그 내용 |
|--------|-----------|
| nginx | 접속 기록 (IP, URL, 상태코드, 응답시간) |
| web | gunicorn 접속 로그 + Django 로그 (INFO 이상) |
| db | 접속 오류, 느린 쿼리 |

> 컨테이너 로그는 **stdout 으로 출력** → Docker 가 수집 (`PYTHONUNBUFFERED=1` 의 이유)

---

# 로그 레벨 조절

`config/settings/base.py`

```python
LOGGING = {
    ...
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
}
```

```bash
# 서버 .env 에 추가 후 재기동 → 더 자세한 로그
echo "DJANGO_LOG_LEVEL=DEBUG" >> .env
dc up -d web
```

<div class="callout warning">
<div class="callout-title">주의</div>
DEBUG 로그는 양이 많고 민감정보가 섞일 수 있습니다. 문제 확인 후 INFO 로 되돌리세요.
</div>

---

# 3) 헬스체크 & 모니터링

```bash
curl -s http://<EC2_IP>/health/
# {"status": "ok", "database": "ok"}
```

| 수준 | 방법 | 도구 예시 |
|------|------|-----------|
| 컨테이너 | `healthcheck` → 자동 상태 표시 | Docker |
| 외부 감시 | 1~5분마다 `/health/` 호출, 실패 시 알림 | UptimeRobot, Better Stack |
| 메트릭 | CPU, 메모리, 요청 수, 응답 시간 | CloudWatch, Prometheus + Grafana |
| 에러 추적 | 예외 발생 시 스택트레이스 수집 | Sentry |

> 💡 실습: 무료 외부 모니터링 서비스에 `http://<EC2_IP>/health/` 를 등록해 보세요

---

# 4) 장애 상황 실습

**버그가 있는 버전이 배포되었다면?**

```python
# 예) config/views.py 를 실수로 수정
def health(request):
    raise Exception("oops")
```

- CI 에서 테스트가 잡아줌 → **배포 안 됨** ✅ (테스트의 가치!)
- 그런데 테스트가 못 잡는 문제라면? (설정 누락, 외부 서비스 장애 …)
  - `deploy.sh` 헬스체크 실패 → **CD job 실패**로 알림
  - 서비스가 이상하다는 신고 → **롤백**

---

# 5) 롤백 : rollback.sh

```bash
TARGET_TAG="${1:-$(grep '^PREVIOUS_IMAGE_TAG=' .env | cut -d= -f2 || true)}"
if [ -z "$TARGET_TAG" ]; then
    echo "[ERROR] 되돌릴 버전이 없습니다. 사용법: bash rollback.sh <이미지 태그>"
    exit 1
fi

IMAGE="$(grep '^IMAGE=' .env | cut -d= -f2)"
echo "[ROLLBACK] $IMAGE:$TARGET_TAG"

# deploy.sh 를 재사용 (태그만 바꿔서 다시 배포)
IMAGE="$IMAGE" IMAGE_TAG="$TARGET_TAG" bash deploy.sh
```

```bash
cd ~/todo-api
bash rollback.sh                   # 직전 버전으로
bash rollback.sh a81b20f4c3...     # 특정 커밋 버전으로
```

---

# 롤백 동작 원리

```
배포 이력 (서버 .env)

  1차 배포:  IMAGE_TAG=aaa111
  2차 배포:  IMAGE_TAG=bbb222   PREVIOUS_IMAGE_TAG=aaa111
              ↓ 장애 발생!
  롤백:      IMAGE_TAG=aaa111   PREVIOUS_IMAGE_TAG=bbb222
```

- 이미지가 **SHA 태그로 GHCR 에 모두 보관**되어 있기 때문에 가능
- 롤백 후 **원인 수정 → 테스트 추가 → 새 PR** 로 정상화 (Roll forward)

<div class="callout warning">
<div class="callout-title">DB 마이그레이션 주의</div>
롤백은 <b>코드만</b> 되돌립니다. 컬럼 삭제 같은 마이그레이션은 되돌리기 어려우므로,
"컬럼 추가 → 코드 배포 → 나중에 삭제" 처럼 <b>호환되는 순서</b>로 나누어 배포하세요.
</div>

---

# 6) PostgreSQL 백업

```bash
cd ~/todo-api
mkdir -p backups

# 백업 (pg_dump → 서버 파일)
dc exec -T db sh -c 'pg_dump --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > backups/todo_$(date +%Y%m%d_%H%M).sql

ls -lh backups/
```

```bash
# 내 PC 로 백업 파일 내려받기
scp -i deploy_key ubuntu@<EC2_IP>:~/todo-api/backups/*.sql ./
```

- `-T` : TTY 없이 실행 (파일로 리다이렉트할 때 필요)
- `--clean --if-exists` : 복원 시 기존 테이블을 지우고 다시 만드는 SQL 포함 → **덮어쓰기 복원 가능**

---

# 백업 복원 & 자동화

```bash
# 복원 (주의: 현재 데이터가 백업 시점으로 덮어써짐)
cat backups/todo_20261113_1000.sql | \
  dc exec -T db sh -c 'psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

```bash
# 매일 새벽 3시 자동 백업 (crontab -e)
0 3 * * * cd ~/todo-api && docker compose -f docker-compose.prod.yml exec -T db \
  sh -c 'pg_dump --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > backups/todo_$(date +\%Y\%m\%d).sql
```

<div class="callout info">
<div class="callout-title">백업 원칙</div>
백업은 <b>복원해 봐야</b> 백업입니다. 서버와 다른 곳(S3 등)에도 보관하세요.
</div>

---

# 7) 서버 정리 & 유지보수

```bash
docker system df                   # Docker 디스크 사용량
docker image prune -f              # 사용하지 않는 이미지 삭제 (deploy.sh 가 자동 수행)
sudo apt update && sudo apt upgrade -y   # OS 보안 업데이트 (정기적으로)
```

| 하지 말 것 | 이유 |
|-----------|------|
| `dc down -v` | **운영 DB 데이터 삭제!** |
| 서버에서 코드 / compose 직접 수정 | 다음 배포 때 덮어써짐, 기록 없음 |
| 서버에서 `docker build` | 이미지 버전 추적 불가 |

---

# 전체 파이프라인 회고

```
 ① Issue 작성          (Plan)        GitHub Issues
 ② 브랜치 + 테스트 먼저  (Code/Test)  pytest, TDD
 ③ 구현 + pre-commit   (Code)        ruff
 ④ PR + 리뷰            (Code)        GitHub PR, 템플릿
 ⑤ CI 자동 검증         (Test)        Actions: ruff → pytest(PostgreSQL) → docker build
 ⑥ merge               (Release)     Branch protection
 ⑦ CD 자동 배포         (Deploy)      GHCR + SSH + deploy.sh
 ⑧ 헬스체크 · 로그       (Operate)     healthcheck, docker logs
 ⑨ 모니터링 · 롤백       (Monitor)     rollback.sh, 백업
        └──▶ 다시 ① 로 (Feedback)
```

---

# 우리가 자동화한 것들

| 이전 (수동) | 이후 (자동) |
|-------------|-------------|
| "테스트 돌려봤어요?" | PR 마다 CI 가 자동 실행 |
| 코드 스타일 지적 | pre-commit + ruff |
| 서버에 접속해 git pull, 재시작 | merge 하면 자동 배포 |
| 서버마다 다른 환경 | 같은 Docker 이미지 |
| 배포 후 "잘 되나?" 직접 확인 | 헬스체크로 자동 검증 |
| 장애 시 우왕좌왕 | `bash rollback.sh` |

---

# 확장 과제

| 주제 | 내용 |
|------|------|
| **HTTPS** | 도메인 연결 + Let's Encrypt(certbot) 인증서, Nginx 443 |
| **무중단 배포** | Blue-Green, 롤링 업데이트 (web 2개 + Nginx 전환) |
| **환경 분리** | staging 서버 → 확인 후 production 승인 배포 (GitHub Environments) |
| **관리형 DB** | PostgreSQL → AWS RDS (자동 백업, 고가용성) |
| **IaC** | Terraform 으로 EC2 · 보안그룹을 코드로 생성 |
| **관측성** | Sentry 에러 추적, Prometheus + Grafana 대시보드 |
| **보안** | 의존성 취약점 스캔(Dependabot), 이미지 스캔(Trivy) |

---

# 실습 마무리 체크리스트

- [ ] 서버에서 `dc ps`, `dc logs` 로 상태 확인
- [ ] 일부러 두 번 배포 후 `bash rollback.sh` 로 되돌리기
- [ ] `pg_dump` 로 백업 파일 생성 & 내려받기
- [ ] 외부 모니터링 서비스에 `/health/` 등록 (선택)
- [ ] **EC2 인스턴스 중지 / 종료** (비용 발생 방지!)
- [ ] GHCR 패키지, GitHub Secrets 정리 (필요 시)

---

# 정리

- DevOps 는 도구가 아니라 **빠르고 안전한 피드백 루프를 만드는 방식**
- **테스트(TDD)** → 신뢰, **자동화(CI/CD)** → 속도, **관찰(로그·헬스체크)** → 안정성
- 문제가 생겨도 **롤백 + 백업**으로 빠르게 복구
- 작게 시작해서 **조금씩 자동화**를 늘려 가세요

---

<!-- _class: lead -->

# 수고하셨습니다 🎉

## Plan → Code → Build → Test → Release → Deploy → Operate → Monitor → ♾️
