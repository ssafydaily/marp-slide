---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

# GitHub Actions

> **GitHub Actions** 는 GitHub에 내장된 **CI/CD** (지속적 통합/지속적 배포) 플랫폼입니다.
> - 코드 푸시, PR 생성, 이슈 등록 등 GitHub의 이벤트에 반응하여 자동으로 워크플로우를 실행합니다.


## 주요 특징

- *무료 사용량* : 공개 저장소 무제한, 비공개 저장소 월 2,000분 (무료 플랜)
- *다양한 실행 환경* : Ubuntu, Windows, macOS 지원
- *풍부한 마켓플레이스* : 수만 개의 커뮤니티 Action 활용 가능
- *GitHub와 완벽 통합* : PR, 이슈, 릴리스와 직접 연동

-------------

# 핵심 개념

<div class="cols-4060">
<div>

```plaintext
저장소 (Repository)
└── .github/
    └── workflows/
        ├── ci.yml     ← workflow 파일
        └── deploy.yml ← 워크플로우 파일
```

</div>
<div>

| 개념 | 설명 | 비유 |
|------|------|------|
| **Workflow** | 자동화 전체 프로세스 | 레시피 전체 |
| **Event** | 워크플로우를 실행시키는 트리거 | 요리 시작 신호 |
| **Job** | 워크플로우 내의 독립적인 작업 단위 | 요리의 각 단계 |
| **Step** | Job 내의 개별 명령 | 세부 조리 동작 |
| **Action** | 재사용 가능한 단위 작업 | 조리 도구 |
| **Runner** | 워크플로우를 실행하는 서버 | 주방 |

</div>
</div>


-------------


# 첫 번째 워크플로우 작성하기

#### 1단계: Github 저장소 생성

1. github.com 에 로그인 후 우측 상단 + `→ New repository` 클릭
2. 다음과 같이 설정합니다.

   | 항목 | 값 |
   |------|-----|
   | Repository name | `my-first-actions` (원하는 이름) |
   | Visibility | Public (무료로 Actions 무제한 사용) |
   | Initialize this repository | ✅ **Add a README file** 체크 |

3. `Create repository` 클릭

> `README.md`를 포함해 생성하면 `master` 브랜치가 바로 만들어집니다.
> 이후 `push` 트리거가 즉시 동작할 수 있습니다.

------------------

#### 2단계: 로컬에 저장소 클론

```bash
# 본인 GitHub 계정명으로 변경

git clone https://github.com/<계정명>/my-first-actions.git

cd my-first-actions
```

#### 3단계: 워크플로우 파일 생성

- `GitHub Actions`는 `.github/workflows/` 폴더 안의 `.yml` 파일을 자동으로 인식합니다.
- `.github/workflows/hello.yml` 파일을 생성


------------------

- YAML 주의사항: 들여쓰기는 반드시 공백만 사용. 탭은 오류를 발생시킵니다.

```yaml
name: Hello World   # workflow name
on:
  push:
    branches: [ master ]   # trigger workflow on push to master branch

jobs:
  say-hello:
    runs-on: ubuntu-latest   # specify the runner environment

    steps:
      - name: 인사하기
        run: echo "안녕하세요, GitHub Actions!"   # print a greeting message
      
      - name: 현재 날짜 출력
        run: date   # print the current date and time
      
      - name: 환경 정보 확인
        run: |
            echo "OS: $RUNNER_OS"
            echo "브랜치: $GITHUB_REF_NAME"
            echo "커밋: $GITHUB_SHA"
```

-------------------

#### 4단계: 커밋 & 푸시

```bash
git add .github/workflows/hello.yml
git commit -m "ci: 첫 번째 GitHub Actions 워크플로우 추가"
git push origin master
```

<div class="callout tip">
  <div class="callout-title">
    `on.push`
  </div>
  push 순간 `on.push` 트리거가 감지되어 워크플로우가 실행됩니다.
</div>

#### 실행 결과 확인
1. `GitHub 저장소 페이지`에서 상단 `Actions 탭` 클릭
2. 왼쪽 목록에서 `Hello World 워크플로우` 선택
3. 가장 최근 실행 항목 클릭 → `say-hello Job` 클릭
4. 각 Step을 클릭하면 실행 로그를 확인할 수 있습니다.

------------

### 실행 흐름 

```
git push
  │
  ▼
GitHub이 push 이벤트 감지
  │
  ▼
.github/workflows/hello.yml 읽기
  │
  ▼
ubuntu-latest Runner(가상 서버) 할당
  │
  ▼
say-hello Job 실행
  ├─ Step 1: 인사하기
  ├─ Step 2: 현재 날짜 출력
  └─ Step 3: 환경 정보 확인
  │
  ▼
Actions 탭에서 결과 확인 (성공 ✅ / 실패 ❌)
```

--------------

