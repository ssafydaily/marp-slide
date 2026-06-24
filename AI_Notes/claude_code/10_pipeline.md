---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

# 실습 

- 하나의 Python 프로젝트를 만들고, 코드 수정부터 로컬 테스트, 서브에이전트 리뷰, 문서 동기화, 커밋, PR 생성, GitHub Actions CI 리뷰까지 하나의 파이프라인으로 엮어 전체가 자동으로 흘러가도록 구축

## 실습 프로젝트 준비

- Claude에게 요청하지 않고 직접 실행

```bash
mkdir claude-code-guide-practice && cd claude-code-guide-practice
git init
python3 -m venv .venv && source .venv/bin/activate
pip install ruff mypy pytest
```
- **ruff** 는 코드 스타일 검사(린트), **mypy** 는 타입 오류 검사, **pytest** 는 테스트 실행을 담당


-----------------------
## 시작 코드 요청

```
ex_pipeline.py에 add 함수를 만들고, test_pipeline.py에 테스트를 작성해줘.
pyproject.toml에 ruff, mypy 설정도 추가해줘.
전부 통과하면 초기 커밋까지 해줘.
```
- `pyproject.toml` 설정은 Claude Code가 알아서 추가할 수도 있지만, 확실하게 해야 하므로 명확하게 지시

- PR을 만들려면 GitHub 리포지토리가 필요하다
  ```
  GitHub repo 만들고 push해줘
  ```
  - GitHub 계정에 로그인되어 있고 `gh CLI` 가 설치되어 있으면 Claude Code가 리포지토리 생성부터 push까지 처리
  - `gh` 가 없으면 설치

---------------------

## 전체 구조


```
코드 수정 (ex_pipeline.py에 기능 추가)
  → ruff check (린트)
  → mypy (타입 검사)
  → pytest (테스트)
  → 서브에이전트 코드리뷰 (커밋 전 로컬 검증)
  → 문서 업데이트 (README.md)
  → Hooks 자동 검사 (커밋 시 위 3개 재실행)
  → 커밋 + PR 생성
  → GitHub Actions 자동 리뷰 (PR 생성 시 Claude가 자동 코멘트)
```
- 각 단계마다 하나씩 설정한 뒤, 마지막에 전체를 한 번에 실행

---------------------
## Git Hook으로 커밋 전 자동 검사

- 커밋 전에 ruff, mypy, pytest를 자동 실행하는 Git pre-commit hook을 설정

  ```
  git commit 전에 ruff check, mypy, pytest를 순서대로 실행하는 Hook을 추가해줘.
  하나라도 실패하면 커밋을 차단해야 해.
  ```
- `.git/hooks/pre-commit.py` 가 생성

## 안전 장치 축
-  Claude Code 자체 Hook을 추가하면 Claude가 도구를 쓰는 모든 순간에 개입할 수 있다
- 위험한 명령어 차단하는 예시

```
위험한 Bash 명령을 차단하는 Claude Code Hook을 추가해줘.
rm -rf, DROP TABLE, git push --force 같은 명령은 실행 전에 막아야 해.
```

------------------------

## 코드 작성 및 검증

- 먼저, 구현과 테스트만 진행

```
@ex_pipeline.py에 divide 함수를 추가해줘.
- 0으로 나누면 ValueError를 발생시켜
- @test_pipeline.py에 테스트도 추가해줘
- ruff check, mypy, pytest 전부 통과하는지 확인해줘
- 아직 커밋하지 마
```

-----------------------

## 코드 리뷰 - 서브에이전트

- 이 단계는 Hook으로 자동화하지 않고 필요할 때 수동으로 실행
- 린트나 테스트와 달리 LLM 호출은 시간과 토큰 비용이 들기 때문에 매 커밋마다 자동 실행하면 비용 부담 발생
- PR 단위의 자동 리뷰는 GitHub Actions가 담당

**코드 리뷰 에이전트 작성**

```
코드리뷰 전문 에이전트를 만들어줘.
보안 취약점, 타입 안전성, 에러 핸들링을 중점적으로 검사하는 역할이야.
.claude/agents/code-reviewer.md에 저장해줘.
```

---------------

- 에이전트가 생성되면 방금 작성한 코드를 리뷰
- `/agents` 를 입력해서 사용가능한 에이전트 목록 확인 
  - 직접 작성한 경우 세션 재시작 필요

**코드 리뷰**
```
code-reviewer 에이전트로 ex_pipeline.py의 divide 함수를 리뷰해줘.
에러 핸들링에 집중해줘.
문제가 있으면 바로 수정해줘.

```
- 커밋 전에 리뷰를 거치므로 PR에 올라가는 코드의 품질이 한 단계 올라감

-----------------

## GitHub Actions 자동 리뷰 설정

- GitHub Actions 워크플로우를 먼저 설정
- 워크플로우가 등록되어 있어야 PR 생성 시 자동으로 CI 리뷰가 트리거된다.

> 인증 키를 GitHub Secrets에 등록
> - **API 키 방식**: Anthropic Console에서 발급한 API 키를 `ANTHROPIC_API_KEY` 로 등록 (**종량제 과금**)
> - **OAuth 토큰 방식**: 터미널에서 `claude setup-token` 을 실행하여 생성한 토큰을 `CLAUDE_CODE_OAUTH_TOKEN` 으로 등록 (**Claude 구독 사용**)

- 토큰 발급하기

```bash
# 토큰 발급
claude setup-token

# 토큰 세팅(보안 주의, 직접 설정 권장)
gh secret set CLAUDE_CODE_OAUTH_TOKEN

```


--------------------

**인증키 등록**

1. GitHub 저장소 > Settings > Secrets and variables > Actions
2. New repository secret 클릭
3. Name: `ANTHROPIC_API_KEY` 또는 `CLAUDE_CODE_OAUTH_TOKEN`, Secret: 키 값

## 참고

- GitHub Secrets에는 Repository Secret과 Environment Secret이 있다. 
- Repository Secret은 레포 내 모든 워크플로우에서 바로 사용
- Environment Secret은 특정 환경(production 등)에 묶여 승인 규칙을 설정할 수 있다.

> 코드 리뷰는 환경 구분이 필요 없으므로 Repository Secret으로 충분

---------------------

## 워크플로우 파일 요청

```
PR이 열리면 Claude가 자동으로 코드리뷰하는 GitHub Actions 워크플로우를 만들어줘.
파일명은 claude-review.yml로 해줘.
anthropics/claude-code-action@v1 공식 액션을 사용해.
actions/checkout은 @v5를 사용해.
```

- 생성된 파일을 확인하고, 오류는 수정한다. 흔한 실수:

  - Claude가 `curl` 로 *Anthropic API* 를 직접 호출하는 커스텀 스크립트를 만드는 경우 - bash에서 변수 이스케이프 문제로 command not found 에러가 발생합니다. 
  - 반드시 공식 액션(`anthropics/claude-code-action@v1`)을 사용
  - `actions/checkout@v4`를 사용하는 경우 - Node.js 20 지원 종료로 경고가 발생. `@v5`를 사용한다.
  - 존재하지 않는 액션 이름(anthropics/anthropic-sdk-action 등)을 생성하는 경우 
    - `uses:` 확인 

- Claude에게 `claude-review.yml` 을 커밋하고 푸시하라고 요청

---------------------

## 커밋과 PR 생성

- 코드, 리뷰, 문서가 모두 준비되고 GitHub Actions 설정도 끝나면 커밋하고 PR을 생성

```
변경된 파일 전부 커밋하고 PR을 만들어줘.
PR 본문에는 변경 이유와 테스트 결과를 포함해.
```

**Claude Code가 다음 순서로 진행**

- 커밋 시 Git pre-commit Hook이 ruff, mypy, pytest를 자동 실행
- 전부 통과하면 커밋 완료
- 브랜치 생성, 푸시, PR 생성
- PR 생성과 동시에 GitHub Actions가 트리거되어 자동 리뷰 시작
- 이때 Git Hook이 동작하여 한 번 더 검사를 수행
- 테스트 통과하면 문제없이 커밋
- PR이 생성되면 1-2분 후 PR 페이지의 Comments 탭에서 Claude의 리뷰 코멘트를 확인

---------------------

## 주의

> Claude가 처리한 내용

- Github App에 Claude 앱 설치 필요

- 인증	git 자격증명 헬퍼가 잘못된 캐시 계정 사용 
  → push 404	gh auth setup-git으로 자격증명 소스를 gh 활성 계정과 일치시킴

- 인증 OAuth 토큰에 workflow 스코프 부재 
  - `.github/workflows/*.yml` 파일을 생성/수정하려면 PAT에 workflow scope가 필요
  → 워크플로우 파일 push 거부	`gh auth refresh -s workflow`로 디바이스 인증을 재진행해 스코프 추가
  ```
  laude Code (또는 스크립트)
    ↓
  GitHub API로 .github/workflows/ 파일 push 시도
      ↓
  PAT에 workflow scope 없음 → 거부
  ```
------------------------

## 리뷰 결과 확인과 머지

- 문제가 없는 경우: PR을 머지합니다.

```
PR을 머지해줘
```

- 수정이 필요한 경우: Claude의 리뷰 코멘트를 참고하여 수정

```
PR 리뷰에서 지적된 사항을 확인하고 수정해줘.
수정 후 테스트 통과하면 다시 커밋해줘.
```
