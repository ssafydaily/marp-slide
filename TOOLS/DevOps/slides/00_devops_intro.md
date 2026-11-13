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

# DevOps 입문

## Django REST Framework 프로젝트로 배우는 개발 → 배포 자동화

---

# 학습 목표

- DevOps 가 **왜** 등장했고 **무엇을** 해결하려는지 설명할 수 있다
- DevOps 라이프사이클(무한 루프)의 각 단계를 이해한다
- CI / CD 의 차이를 설명할 수 있다
- 이번 과정에서 만들 **Todo API 파이프라인** 전체 그림을 이해한다

---

# 이런 경험 있나요?

- "제 컴퓨터에서는 잘 되는데요?" 🤔
- 배포하는 날 = 야근하는 날
- 누가 언제 무엇을 바꿨는지 모름
- 버그를 고쳤더니 다른 곳이 깨짐
- 서버 설정 방법이 **한 사람 머릿속에만** 있음

<div class="callout warning">
<div class="callout-title">문제의 본질</div>
개발(Dev)과 운영(Ops)이 분리되어, 변경 사항이 사용자에게 전달되기까지 <b>느리고 위험</b>하다.
</div>

---

# Dev vs Ops : 사일로(Silo) 문제

<div class="cols">
<div>

### 개발팀 (Dev)
- 목표: **빠른 변화**
- 새 기능을 빨리 내보내고 싶다
- "코드는 다 짰어요, 이제 운영팀 일"

</div>
<div>

### 운영팀 (Ops)
- 목표: **안정성**
- 변경은 곧 장애의 원인
- "배포는 한 달에 한 번만 합시다"

</div>
</div>

> 서로 다른 목표 → 벽(Wall of Confusion) → 느린 배포, 잦은 장애, 책임 전가

---

# DevOps 란?

> **개발(Development)과 운영(Operations)의 경계를 허물고,
> 소프트웨어를 빠르고 안정적으로 전달하기 위한 문화 · 프로세스 · 도구의 결합**

- 특정 도구나 직무 이름이 아니라 **일하는 방식**
- 핵심: **자동화 + 협업 + 빠른 피드백**
- 결과: 작은 변경을 **자주, 안전하게** 배포

---

# DevOps 의 핵심 가치 : CALMS

| 요소 | 의미 | 이번 실습에서 |
|------|------|--------------|
| **C**ulture | 협업, 공동 책임 | PR · 코드 리뷰 |
| **A**utomation | 반복 작업 자동화 | pytest, GitHub Actions |
| **L**ean | 작게, 자주 | 기능 브랜치, 작은 PR |
| **M**easurement | 측정 · 모니터링 | 커버리지, 헬스체크, 로그 |
| **S**haring | 지식 공유 | README, 템플릿, IaC |

---

# DevOps 라이프사이클 (무한 루프)

```
          ┌──────── Dev ────────┐        ┌──────── Ops ────────┐
          │                     │        │                     │
   Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
     ↑                                                          │
     └──────────────────── 피드백 (Feedback) ─────────────────────┘
```

| 단계 | 하는 일 | 사용할 도구 |
|------|---------|------------|
| Plan | 요구사항, 이슈 관리 | GitHub Issues |
| Code | 코드 작성, 버전관리 | Git, GitHub |
| Build / Test | 빌드, 자동 테스트 | pytest, Docker |
| Release / Deploy | 배포 자동화 | GitHub Actions, GHCR |
| Operate / Monitor | 운영, 관찰 | Docker Compose, Nginx, 로그 |

---

# CI / CD

<div class="cols">
<div>

### CI : Continuous Integration
**지속적 통합**
- 코드를 자주 main 에 합친다
- 합칠 때마다 **자동으로 빌드 + 테스트**
- 문제를 **일찍** 발견

</div>
<div>

### CD : Continuous Delivery / Deployment
**지속적 전달 / 배포**
- 테스트를 통과한 코드를 **언제든 배포 가능한 상태로** 유지
- Deployment: 운영 서버까지 **자동 배포**

</div>
</div>

```
코드 push → [CI] 린트 · 테스트 · 빌드 → [CD] 이미지 저장 → 서버 배포 → 헬스체크
```

---

# 왜 TDD 가 DevOps 와 연결될까?

- 자동화된 파이프라인은 **테스트를 믿고** 배포한다
- 테스트가 없다면 → CI 는 "빌드만 되는지" 확인할 뿐
- **TDD (Test Driven Development)**
  1. 🔴 **Red** : 실패하는 테스트를 먼저 작성
  2. 🟢 **Green** : 테스트를 통과하는 최소한의 코드
  3. 🔵 **Refactor** : 테스트를 유지하며 코드 개선

<div class="callout tip">
<div class="callout-title">TIP</div>
테스트 = 배포 안전장치. "테스트가 통과하면 배포해도 된다"는 신뢰가 DevOps 의 기반입니다.
</div>

---

# 실습 프로젝트 : Todo API

- **Django REST Framework** 로 만드는 할 일 관리 API
- DB: **PostgreSQL** (Docker 컨테이너로 실행)

| Method | URL | 기능 |
|--------|-----|------|
| GET | `/api/todos/` | 목록 (`?is_done=`, `?search=`) |
| POST | `/api/todos/` | 생성 |
| GET / PUT / PATCH / DELETE | `/api/todos/{id}/` | 상세 / 수정 / 삭제 |
| GET | `/health/` | 서버 + DB 상태 확인 |

---

# 실습 로드맵

| Step | 주제 | DevOps 단계 |
|------|------|------------|
| 1 | 개발 환경 구성 (Django + PostgreSQL) | Code |
| 2 | TDD & pytest 기초 – 모델 | Code / Test |
| 3 | DRF API TDD | Code / Test |
| 4 | Git & GitHub 협업 | Plan / Code |
| 5 | 코드 품질 자동화 (ruff, pre-commit) | Code / Test |
| 6 | Docker 컨테이너화 | Build |
| 7 | CI – GitHub Actions | Test / Release |
| 8 | 서버 준비 & CD (EC2 자동 배포) | Deploy |
| 9 | 운영 & 마무리 (로그, 롤백) | Operate / Monitor |

---

# 최종 완성 모습

```
 개발자 PC                    GitHub                         AWS EC2
┌──────────┐  push/PR  ┌─────────────────────┐  SSH   ┌──────────────────────┐
│ 코드 작성 │ ───────▶ │ CI: ruff → pytest    │ ─────▶ │ Nginx :80             │
│ pytest   │           │      → docker build │        │   └▶ web (gunicorn)   │
│ pre-commit│          │ CD: image → GHCR    │        │        └▶ PostgreSQL  │
└──────────┘           └─────────────────────┘        └──────────────────────┘
```

- main 에 merge 하면 **몇 분 안에 운영 서버에 자동 반영**
- 실패하면 배포되지 않고, 문제가 생기면 **이전 버전으로 롤백**

---

# 실습 자료 구성

```
TOOLS/DevOps/
├── slides/                  # 지금 보고 있는 슬라이드
└── practice/
    ├── step01_setup/
    │   ├── template/        # 실습 시작 코드 (TODO 를 채운다)
    │   └── solution/        # 완성 코드
    ├── step02_model_tdd/
    └── ...
```

<div class="callout info">
<div class="callout-title">진행 방법</div>
각 Step 의 <code>template/</code> 에서 TODO 를 채워 테스트를 통과시키고, 막히면 <code>solution/</code> 과 비교합니다.
</div>

---

# 사전 준비물

- **Python 3.11**
- **Git** + **GitHub 계정**
- **Docker Desktop** (Windows: WSL2 기반) — PostgreSQL 을 컨테이너로 실행
- **VS Code** (Python 확장)
- (Step 8) **AWS 계정** — EC2 프리티어

```bash
python --version          # Python 3.11.x
git --version
docker --version
docker compose version
```

---

# 정리

- DevOps = Dev 와 Ops 의 벽을 허무는 **문화 + 프로세스 + 자동화**
- 핵심 흐름: Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
- **CI** 는 통합할 때마다 자동 검증, **CD** 는 검증된 코드를 자동 배포
- **TDD** 로 만든 테스트가 파이프라인 신뢰의 기반

### 다음 시간 ▶ Step 1. 개발 환경 구성
