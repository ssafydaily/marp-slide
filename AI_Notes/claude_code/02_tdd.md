---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

## TDD 워크플로우

- "테스트 먼저 작성해줘"라고 단계를 나누면 **Red-Green-Refactor**가 정확히 동작

## 준비

```
TDD 연습용 Node.js 프로젝트를 세팅해줘.
npm init, jest 설치, src 폴더 생성, scripts.test를 "jest --verbose"로 설정해줘.
```

## Red 

- 이메일 유효성 검사 함수를 TDD로 만듭니다. 
--------

- 핵심은 "테스트를 먼저 작성해줘. 구현은 아직 하지 마."라는 문장입니다.

```
이메일 유효성 검사 함수 validateEmail(email)을 만들 겁니다.

요구사항:
- 유효한 이메일이면 { valid: true }를 반환
- 유효하지 않으면 { valid: false, reason: "에러 메시지" }를 반환
- 검사 항목: @ 포함, @ 앞뒤 문자 존재, 도메인에 점 포함, 공백 불가, null/빈 문자열 불가

테스트를 먼저 작성해줘. 구현은 아직 하지 마.
파일: src/validateEmail.test.js
```

- 테스트를 실행해서 실패 확인
```
테스트 실행해줘
```
---------

## Green - 최소한 구현

- 테스트를 통과하는 구현을 요청

```
@src/validateEmail.test.js의 모든 테스트를 통과하는 최소한의 구현을 작성해줘.
파일: src/validateEmail.js
과도한 최적화나 추가 기능은 넣지 마.
```
### 엣지 케이스 추가

```
@src/validateEmail.test.js에 엣지 케이스 테스트를 추가해줘:
- 특수문자 포함 이메일 (user+tag@domain.com)
- 연속된 점 (user@domain..com)
- 매우 긴 이메일 주소

추가한 테스트가 실패하면 @src/validateEmail.js 구현도 함께 수정해줘.
```

---------

## Refactor

- 테스트가 모두 통과하는 상태에서 코드 품질을 개선

```
@src/validateEmail.js를 리팩토링해줘.
@src/validateEmail.test.js의 모든 테스트가 통과하는 상태를 유지하면서:
1. 가독성 개선
2. 에러 메시지를 더 구체적으로
3. 유지보수하기 쉬운 구조로 변경

리팩토링 후 테스트를 실행해서 통과하는지 확인해줘.
```

- Refactor 단계에서는 기능을 추가하지 않는다. 
- 동작은 유지하고 코드 품질만 개선

-------

## 주의 사항

<div class="callout warning ">
  <div class="callout-title">
    
  주의 사항

  </div>

  - 테스트가 실패하는 것을 반드시 확인한 후 구현을 시작
  - 한 사이클에 하나의 기능만 처리
  - Red-Green-Refactor를 작은 단위로 반복
  - 테스트와 구현을 동시에 요청하지 않는다

</div>

----------------

# 리팩토링

- "중복 코드 정리해줘"라고 시키면, Claude가 여러 파일을 한꺼번에 바꿔서 뭐가 달라졌는지 파악이 안 됩니다. 
- *계획을 먼저* 세우고, *파일 단위로 진행* 하면 안전합니다.

## 확인

- 현재 상태를 확인

```
git status를 확인해줘. 커밋되지 않은 변경사항이 있으면 먼저 커밋해줘.

````

-----------


## 중복 코드 탐색
- Claude가 프로젝트를 분석하고 유사 패턴이 반복되는 위치를 목록으로 정리

```
이 프로젝트에서 중복되거나 유사한 코드 패턴을 찾아줘.
3번 이상 반복되는 것 위주로, 파일명과 줄 번호를 포함해서 보여줘.
  
```

## 계획 확인

-바로 수정하지 말고, 계획을 먼저 확인
```
이 중복들을 어떻게 리팩토링할지 계획만 세워줘. 코드는 아직 수정하지 마.
```
- Claude가 공통 함수 추출, 유틸리티 모듈 분리 등의 전략을 제안합니다. 계획이 의도와 다르면 방향을 수정합

```
fetch 관련 함수만 공통 함수로 추출해줘. 나머지는 그대로 둬.
```
---------

## 실행

```
계획대로 리팩토링 진행해. 한 파일씩 수정하고 각 변경사항을 설명해줘.
```

## 확인과 커밋
```
변경된 부분의 테스트를 실행해줘. 테스트가 없으면 만들어서 실행해줘.

```
- 테스트 통과하면 커밋한다.

```
리팩토링 변경사항을 확인하고, 무엇을 왜 바꿨는지 포함해서 커밋해줘.
```

-----------

<div class="callout tip">
  <div class="callout-title">
  
  주의 사항

  </div>

  - 리팩토링 전에 반드시 커밋 상태를 확인한다.
  - 되돌릴 수 없으면 위험합니다.
  - Claude의 계획을 실행 전에 검토합니다. 
  - 리팩토링 커밋은 기능 변경 커밋과 분리합니다.

</div>

-----------

# Hook

> Hook은 Claude의 동작 시점에 자동으로 실행되는 명령어(4가지 유형)
> - `command`: 셸 명령어를 실행합니다 (가장 일반적)
> - `prompt`: 별도의 Claude 모델(기본 Haiku)에게 프롬프트를 보내 판단(ok/not ok)을 받습니다
> - `agent`: 파일 읽기, 코드 검색 등 도구를 사용할 수 있는 서브에이전트를 호출하여 다단계 검증을 수행합니다
> - `http`: 지정한 URL로 JSON을 POST 전송합니다 (외부 서비스 연동용)

| 구분   | 	CLAUDE.md | 	Hook |
| ----- | --------- | -------- |
| 실행 보장   | 	아닙니다 (무시 가능)| 	보장됩니다 (강제 실행) |
| 설정 위치	   | CLAUDE.md 파일| 	.claude/settings.json의 hooks 필드 |
| 용도   | 	코딩 가이드라인, 스타일 권장| 	포맷팅, 린트, 위험 명령어 차단 |

------------

## 주요 이벤트

- 총 22개의 이벤트가 있음


<div class="cols">
<div>

| 이벤트 | 	실행 시점 |
| ----- | -------- |
| SessionStart | 	세션 시작 또는 재개 시 |
| UserPromptSubmit	 | 프롬프트 제출 후, Claude 처리 전 |
| PreToolUse | 	도구 실행 전 (차단 가능) |
| PermissionRequest | 	권한 다이얼로그 표시 전 |
| PostToolUse | 	도구 실행 후 |
| PostToolUseFailure | 	도구 실행 실패 후 |
| Notification | 	알림 발생 시 |


</div>
<div>

| 이벤트 | 	실행 시점 |
| ----- | -------- |
| Stop | 	턴 종료 시 |
| StopFailure | 	API 오류(속도 제한, 인증 실패 등)로 에이전트 턴이 종료될 때  |(rate_limit, authentication_failed 등 에러 타입으로 매처 지정 가능)
| ConfigChange | 	설정 파일 변경 시 |
| PreCompact | 	컨텍스트 압축 전 |
| PostCompact | 	컨텍스트 압축 완료 후 |
| SessionEnd | 	세션 종료 시 |

</div>
</div>

- Hook 설정을 확인할 때는 Claude Code 안에서 /hooks를 입력하면 이벤트별로 등록된 훅 목록을 볼 수 있다

------------------

## 첫번째 예시

- Claude가 입력을 기다리는 시점에 데스크탑 알림을 보내주는 훅
```
Claude가 작업을 마치고 내 입력을 기다릴 때 윈도우 데스크탑 알림을 보내주는 Hook을 설정해줘.
```
- `~/.claude/settings.json` 에 다음을 추가
  - Claude가 실행 중에 전역 또는 해당 프로젝트에만 적용할 건지 물어본다.
- 설정 후 `/hooks` 를 입력하면 Notification 항목에 훅이 등록된 것을 확인할 수 있다.


----------


```json
{
  // . . .
  "hooks": {
    // . . .
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "async": true,
            "command": "Add-Type -AssemblyName System.Windows.
                             // 생략         
          }
        ]
      }
    ]
  }
}
```

----------------






