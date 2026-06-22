---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---
# Git PR 코드 리뷰

## 사전 준비

- github CLI 가 필요함
```shell
winget install --id GitHub.cli
```
## 커밋 메시지 자동 생성

- 코드 수정후 커밋 요청
```
현재 변경사항을 확인하고 적절한 커밋 메시지로 커밋해줘
```
- Claude가 `git diff`를 분석하고, 변경 내용에 맞는 메시지를 생성하여 커밋

----------

- Conventional Commits 형식(feat:, fix:, docs: 등)을 원하면 프로젝트의 CLAUDE.md에 규칙을 작성

```
## Git 규칙
- 커밋 메시지는 Conventional Commits 형식 (feat:, fix:, docs: 등)
- 영어로 작성, 제목 50자 이내
```

## PRM 생성 
- 커밋 후 PR 생성

```
이 변경 사항으로 PR을 생성해줘. 본문에 변경사항 요약을 포함해.
```
- Claude가 `gh pr create` 를 실행하여 PR을 생성, 제목, 본문, 라벨까지 자동으로 작성합니다
- 더 구체적으로 지정하기
```
PR을 만들어줘. base는 develop, 리뷰어는 @teammate, 라벨은 enhancement
```
----------

## 코드리뷰 받기
- 변경 사항을 Claude에게 리뷰 받기
```
현재 git diff를 리뷰해줘. 버그, 보안, 성능 문제를 중심으로 확인해.
```
- 이전에 PR 작업을 했던 세션을 이어서 리뷰하려면 `--from-pr` 플래그로 Claude Code를 시작

```sh
# PR #42에 연결된 이전 세션을 재개
claude --from-pr 42
```
-----------

## 전체 흐름 한 번에 실행

- `/commit-push-pr` 스킬을 만들어 두었다면 한 줄로 실행할 수 있다

- 또는 프롬프트로 단계별 요청
```
1. 현재 변경사항을 확인해줘
2. Conventional Commits 형식으로 커밋해줘
3. 원격 저장소에 푸시해줘
4. PR을 만들고 변경사항 요약을 본문에 포함해줘
```

----------

<div class="callout tip">
  <div class="callout-title">
  
  주의 사항

  </div>
  
  - Claude가 생성한 커밋 메시지와 PR 본문을 수락하기 전에 내용을 반드시 확인
  - 원격 저장소에 push 권한이 있는지 확인. fork한 저장소라면 origin이 맞는지 확인이 필요.
  - `main/develop` 브랜치에 직접 커밋하지 않도록, CLAUDE.md에 "main 브랜치에 직접 커밋하지 마"와 같은 브랜치 규칙을 작성
  - 커밋 diff에 API 키나 비밀번호가 포함되지 않았는지 확인

</div>

--------------

# Github Actions

## API Key Github Secrets에 등록
- Anthropic API 키를 GitHub Secrets에 등록

<div class="callout info">
  <div class="callout-title">
  
  API 키 등록

  </div>  
  
  1. GitHub 저장소 > Settings > Secrets and variables > Actions
  2. New repository secret 클릭
  3. Name: `ANTHROPIC_API_KEY`, Secret: API 키 값 (console.anthropic.com에서 발급)

</div>

- API 키는 Claude 구독(Pro/Max)과 별도의 종량제 과금. 
- 워크플로우 파일에 직접 작성하면 노출되므로 반드시 Secrets를 사용.

--------------

## 워크 플로우 파일 생성

```
GitHub Actions에서 PR이 열릴 때마다 Claude Code가 자동 코드리뷰를 실행하는 워크플로우를 만들어줘.
파일명은 claude-review.yml로 해줘.
PR 코멘트에 @claude를 포함하면 추가 분석도 가능하도록 해줘.
anthropics/claude-code-action@v1 공식 액션을 사용해.
actions/checkout은 @v5를 사용해.
```

1. PR이 열리거나 커밋이 추가되면 Claude가 변경된 코드를 자동으로 리뷰합니다
2. PR 코멘트에 @claude를 포함하면 Claude가 해당 요청에 대해 분석하고 답변합니다

--------------------

## CLAUDE.md에 리뷰 기준 추가

- 프로젝트 루트의 CLAUDE.md에 리뷰 기준을 작성합니다. 
- GitHub Actions에서 실행되는 Claude도 이 파일을 읽으므로 동일한 규칙을 따릅니다.


```markdown
## 코드리뷰 기준
- 보안: SQL 인젝션, XSS, 인증 우회 점검
- 성능: N+1 쿼리, 불필요한 반복문 점검
- 컨벤션: 네이밍 규칙, import 순서 준수 여부
- 테스트: 새 기능에 테스트가 포함되었는지 확인
```
------------

## PR 올려서 동작 확인
- 파일을 수정하고 PR 생성

## PR 코멘트 입력
```
@claude 이 변경사항에 보안 문제가 있는지 확인해줘
```

> 비용 제한
```
  - name: Run Claude Code
    uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
      claude_args: "--max-turns 3"
```

--------------

## 주의 사항


- API 키는 반드시 GitHub Secrets에 저장합니다.
  - 워크플로우 파일에 직접 넣으면 저장소를 보는 모든 사람에게 노출된다.
- PR마다 Claude API를 호출하므로 비용이 발생
- 사용이 활발한 저장소에서는 `--max-turns` 를 설정하고 사용량을 모니터링
- 테스트가 완료된 후 test/claude-review 브랜치와 PR은 삭제해도 된다.

-----------------

# Git Worktree

- 브랜치를 전환하면 작업 디렉토리가 바뀌고, 실행 중이던 Claude Code 세션도 중단
- **Git Worktree**로 브랜치별로 독립된 디렉토리에서 세션 중단 없이 여러 작업을 동시에 진행

##### `--worktree` 플래그로 세션 생성

- Claude Code에는 Worktree를 자동으로 생성하는 `--worktree`(-w) 플래그가 내장

```sh
claude -w feature-login     # 기능 개발용 세션
claude -w fix-auth-error    # 버그 수정용 세션 (다른 터미널에서)
claude -w refactor-api      # 리팩토링용 세션 (다른 터미널에서)
```

- `-w` 뒤에 이름을 지정하면 `.claude/worktrees/` 아래에 해당 디렉토리가 생성되고, `worktree-feature-login` 같은 브랜치가 자동으로 만들어진다. 
  - 이름을 생략하면 Claude가 랜덤 이름 부여

-------------------

## 여러 터미널에서 병렬 실행

- 각 Worktree 세션을 별도의 터미널 탭이나 창에서 실행합니다. 
- tmux를 사용하면 터미널을 닫아도 세션이 유지됩니다.

```sh
# 터미널 1
claude -w feature-login

# 터미널 2
claude -w fix-auth-error
```
- tmux 사용
```sh
tmux new-session -d -s login 'claude -w feature-login'
tmux new-session -d -s authfix 'claude -w fix-auth-error'
```
----------------

## 병렬로 작업 지시

**터미널 1 (기능 개발):**
```
로그인 폼 컴포넌트를 만들어줘. 이메일과 비밀번호 필드, 유효성 검사를 포함해줘.
```

**터미널 2 (버그 수정):**
```
인증 토큰 만료 시 자동 갱신이 안 되는 버그를 찾아서 수정해줘.
```

**터미널 3 (리팩토링):**
```
src/api/ 디렉토리에서 중복되는 HTTP 요청 코드를 공통 유틸 함수로 추출해줘.
```

----------------

## 작업 모니터링
- 병렬 세션 중 하나에 장시간 작업을 맡기고, /loop으로 주기적으로 상태를 확인

```
/loop 5m PR #42 상태 확인해줘
```


- 5분마다 PR #42의 CI 상태, 리뷰 코멘트, 머지 가능 여부를 자동으로 확인

##### 5+5 병렬 패턴
- *Anthropic* 의 Boris Cherny는 대규모 작업에 **5+5** 패턴을 사
- 로컬 터미널에서 5개의 Worktree 세션을 실행하고, claude.ai/code에서 5~10개의 클라우드 세션을 추가로 실행
  - 총 10~15개의 Claude Code 인스턴스가 동시에 서로 다른 작업을 처리

- 이 패턴의 핵심은 각 **세션에 독립적인 작업을 할당**하여 충돌을 최소화한다.. 
- 파일 수정 영역이 겹치지 않도록 작업을 분배

---------------

## 작업 완료 후 머지

- Worktree 세션에서 작업이 끝나면 Claude에게 커밋과 PR 생성을 요청
- PR 기반 워크플로우를 사용하면 각 Worktree의 변경사항을 독립적으로 리뷰하고 머지할 수 있다

```
현재 변경사항을 커밋하고, PR을 만들어줘
```

- `-w` 플래그로 생성한 Worktree는 세션 종료(`/exit`) 시 자동 정리 여부를 묻습니다. 

```
머지 완료된 worktree를 정리해줘
```
- Claude가 `git worktree list`로 목록을 확인하고, 머지된 Worktree를 `git worktree remove` 로 삭제