# VS Code에서 커스텀 지시사항(Custom Instructions) 사용하기

커스텀 지시사항을 사용하면 AI가 코드를 생성하고 다른 개발 작업을 처리하는 방식에 자동으로 영향을 주는 공통 가이드라인과 규칙을 정의할 수 있습니다. 매번 채팅 프롬프트에 수동으로 컨텍스트를 포함시키는 대신, Markdown 파일에 커스텀 지시사항을 지정해 두면 코딩 관행과 프로젝트 요구사항에 맞는 일관된 AI 응답을 보장할 수 있습니다.

커스텀 지시사항을 모든 채팅 요청에 자동으로 적용되도록 설정할 수도 있고, 특정 파일에만 적용되도록 설정할 수도 있습니다. 또는 특정 채팅 프롬프트에 수동으로 커스텀 지시사항을 첨부할 수도 있습니다.

<div class="docs-action" data-show-in-doc="false" data-show-in-sidebar="true" title="지시사항 생성">

`/init` 을 사용해 프로젝트를 AI에 맞게 설정하면 프로젝트에 맞는 커스텀 지시사항이 생성됩니다.

* [VS Code에서 열기](vscode://GitHub.Copilot-Chat/chat?prompt=%2Finit)

</div>

> [!TIP]
> [Agent Customizations 편집기](/docs/agent-customization/overview.md#manage-customizations-in-the-editor)(프리뷰)를 사용하면 모든 에이전트 커스터마이징을 한 곳에서 검색, 생성, 관리할 수 있습니다. 명령 팔레트에서 **Chat: Open Customizations**를 실행하세요.

> [!NOTE]
> 커스텀 지시사항은 에디터에서 타이핑할 때 표시되는 [인라인 제안](/docs/editing/ai-powered-suggestions.md)에는 적용되지 않습니다.

## 지시사항 파일의 종류

VS Code는 두 가지 범주의 커스텀 지시사항을 지원합니다. 프로젝트에 여러 개의 지시사항 파일이 있는 경우, VS Code는 이를 결합하여 채팅 컨텍스트에 추가하며, 특정한 순서는 보장되지 않습니다.

### 상시 적용 지시사항 (Always-on instructions)

상시 적용 지시사항은 모든 채팅 요청에 자동으로 포함됩니다. 프로젝트 전반의 코딩 표준, 아키텍처 결정, 그리고 모든 코드에 적용되는 관례에 사용하세요.

* 단일 [`.github/copilot-instructions.md`](#use-a-githubcopilot-instructionsmd-file) 파일
    * 워크스페이스의 모든 채팅 요청에 자동으로 적용됨
    * 워크스페이스 내에 저장됨

* 하나 이상의 [`AGENTS.md`](#use-an-agentsmd-file) 파일
    * 워크스페이스에서 여러 AI 에이전트를 함께 사용할 때 유용함
    * 워크스페이스의 모든 채팅 요청 또는 특정 하위 폴더(실험적)에 자동으로 적용됨
    * 워크스페이스 루트 또는 하위 폴더(실험적)에 저장됨

* [조직 수준 지시사항](#share-custom-instructions-across-teams)
    * GitHub 조직 내 여러 워크스페이스와 리포지토리에서 지시사항을 공유
    * GitHub 조직 수준에서 정의됨

* [`CLAUDE.md`](#use-a-claudemd-file) 파일
    * Claude Code 및 기타 Claude 기반 도구와의 호환성을 위함
    * 워크스페이스 루트, `.claude` 폴더, 또는 사용자 홈 디렉터리에 저장됨

### 파일 기반 지시사항 (File-based instructions)

파일 기반 지시사항은 에이전트가 작업 중인 파일이 지정된 패턴과 일치하거나 설명이 현재 작업과 일치할 때 적용됩니다. 언어별 관례, 프레임워크 패턴, 또는 코드베이스의 특정 부분에만 적용되는 규칙에는 파일 기반 지시사항을 사용하세요.

* 하나 이상의 [`.instructions.md`](#use-instructionsmd-files) 파일
    * glob 패턴을 사용하여 파일 유형이나 위치에 따라 조건적으로 지시사항을 적용
    * 워크스페이스 또는 사용자 프로필에 저장됨

지시사항에서 파일이나 URL 같은 특정 컨텍스트를 참조하려면 Markdown 링크를 사용할 수 있습니다.

> [!TIP]
> **어떤 방식을 사용해야 할까요?** 프로젝트 전반의 코딩 표준에는 단일 `.github/copilot-instructions.md` 파일로 시작하세요. 파일 유형이나 프레임워크별로 다른 규칙이 필요하면 `.instructions.md` 파일을 추가하세요. 워크스페이스에서 여러 AI 에이전트를 사용한다면 `AGENTS.md`를 사용하세요.

## `.github/copilot-instructions.md` 파일 사용하기

VS Code는 워크스페이스 루트에 있는 `.github/copilot-instructions.md` Markdown 파일을 자동으로 감지하여 이 파일의 지시사항을 해당 워크스페이스의 모든 채팅 요청에 적용합니다.

`copilot-instructions.md`는 다음과 같은 경우에 사용하세요:

* 프로젝트 전체에 적용되는 코딩 스타일 및 네이밍 규칙
* 기술 스택 선언 및 선호하는 라이브러리
* 따라야 하거나 피해야 할 아키텍처 패턴
* 보안 요구사항 및 에러 처리 방식
* 문서화 표준

워크스페이스에 `.github/copilot-instructions.md` 파일을 만들려면 다음 단계를 따르세요:

1. 워크스페이스 루트에 `.github/copilot-instructions.md` 파일을 생성합니다. 필요하다면 먼저 `.github` 디렉터리를 만드세요.

1. Markdown 형식으로 지시사항을 작성합니다. 최적의 결과를 위해 간결하고 초점이 명확하게 작성하세요.

> [!NOTE]
> VS Code는 상시 적용 지시사항으로 [`AGENTS.md` 파일](#use-an-agentsmd-file) 사용도 지원합니다.

<details>
<summary>예시: 일반적인 코딩 가이드라인</summary>

```markdown
---
applyTo: "**"
---
# 프로젝트 일반 코딩 표준

## 네이밍 규칙
- 컴포넌트 이름, 인터페이스, 타입 별칭에는 PascalCase 사용
- 변수, 함수, 메서드에는 camelCase 사용
- private 클래스 멤버에는 언더스코어(_) 접두사 사용
- 상수에는 ALL_CAPS 사용

## 에러 처리
- 비동기 작업에는 try/catch 블록 사용
- React 컴포넌트에 적절한 에러 바운더리 구현
- 항상 컨텍스트 정보와 함께 에러 로깅
```

</details>

## `.instructions.md` 파일 사용하기

`*.instructions.md` Markdown 파일을 만들어 에이전트가 작업 중인 파일이나 작업에 따라 동적으로 적용되는 파일 기반 지시사항을 만들 수 있습니다.

에이전트는 지시사항 파일 헤더의 `applyTo` 속성에 지정된 파일 패턴 또는 현재 작업과 지시사항 설명의 의미적 일치를 기준으로 어떤 지시사항 파일을 적용할지 결정합니다.

`.instructions.md` 파일은 다음과 같은 경우에 사용하세요:

* 프론트엔드와 백엔드 코드에 대한 서로 다른 관례
* 모노레포에서 언어별 가이드라인
* 특정 모듈에 대한 프레임워크별 패턴
* 테스트 파일이나 문서에 대한 특수 규칙

### 지시사항 파일 위치

특정 워크스페이스 또는 모든 워크스페이스에 적용되는 사용자 수준에서 지시사항을 정의할 수 있습니다. 다음 표는 범위에 따른 지시사항 파일의 기본 위치를 나열합니다. `setting(chat.instructionsFilesLocations)` 설정을 사용하여 워크스페이스 지시사항 파일의 추가 위치를 구성할 수 있습니다.

| 범위 | 기본 파일 위치 |
|-------|-----------------------|
| 워크스페이스 | `.github/instructions` 폴더 |
| 워크스페이스 (Claude 형식) | `.claude/rules` 폴더 |
| 사용자 프로필 | `~/.copilot/instructions`, `~/.claude/rules`, 또는 사용자 데이터(VS Code 프로필에 따라 다름) |

VS Code는 이 폴더들을 재귀적으로 검색하므로 하위 디렉터리에 지시사항 파일을 구성할 수 있습니다. 예를 들어, 팀, 언어, 모듈별로 지시사항을 그룹화할 수 있습니다:

```text
.github/instructions/
  frontend/
    react.instructions.md
    accessibility.instructions.md
  backend/
    api-design.instructions.md
  testing/
    unit-tests.instructions.md
```

다음 예시는 워크스페이스 수준 지시사항만 허용하도록 지시사항 파일 위치를 구성하는 방법을 보여줍니다:

```json
"chat.instructionsFilesLocations": {
  ".github/instructions": true,
  ".claude/rules": true,
  "~/.copilot/instructions": false,
  "~/.claude/rules": false
}
```

> [!TIP]
> 모노레포에서는 `setting(chat.useCustomizationsInParentRepositories)`를 활성화하여 상위 리포지토리 루트의 지시사항을 검색하도록 할 수 있습니다. [상위 리포지토리 검색](/docs/agent-customization/overview.md#use-customizations-in-a-monorepo)에 대해 자세히 알아보세요.

### 지시사항 파일 형식

지시사항 파일은 `.instructions.md` 확장자를 가진 Markdown 파일입니다. 선택적인 YAML 프런트매터 헤더로 지시사항이 적용되는 시점을 제어합니다:

| 필드 | 필수 여부 | 설명 |
|-------|----------|-------------|
| `name` | 아니오 | UI에 표시되는 이름. 기본값은 파일 이름입니다. |
| `description` | 아니오 | Chat 보기에서 호버 시 표시되는 간단한 설명. |
| `applyTo` | 아니오 | 워크스페이스 루트를 기준으로 지시사항이 자동으로 적용될 파일을 정의하는 glob 패턴. 모든 파일에 적용하려면 `**`를 사용하세요. 지정하지 않으면 지시사항이 자동으로 적용되지 않지만 채팅 요청에 수동으로 추가할 수 있습니다. |

본문에는 Markdown 형식의 지시사항이 포함됩니다. 에이전트 도구를 참조하려면 `#tool:<tool-name>` 구문을 사용하세요(예: `#tool:web/fetch`).

```markdown
---
name: 'Python Standards'
description: 'Python 파일에 대한 코딩 관례'
applyTo: '**/*.py'
---
# Python 코딩 표준
- PEP 8 스타일 가이드를 따르세요.
- 모든 함수 시그니처에 타입 힌트를 사용하세요.
- public 함수에는 docstring을 작성하세요.
- 들여쓰기에는 4개의 공백을 사용하세요.
```

### 지시사항 파일 생성하기

지시사항 파일을 만들 때, 워크스페이스 또는 사용자 프로필 중 어디에 저장할지 선택하세요. 워크스페이스 지시사항 파일은 해당 워크스페이스에만 적용되고, 사용자 지시사항 파일은 여러 워크스페이스에서 사용할 수 있습니다.

지시사항 파일을 생성하려면:

> [!TIP]
> 채팅 입력창에 `/instructions`를 입력하면 **Configure Instructions and Rules** 메뉴를 빠르게 열 수 있습니다.

1. Chat 보기에서 **Configure Chat**(톱니바퀴 아이콘)을 선택하여 Agent Customizations 편집기를 열고 **Instructions** 탭을 선택합니다.

1. 드롭다운에서 지시사항 파일을 저장할 위치에 따라 **New Instructions (Workspace)** 또는 **New Instructions (User)**를 선택합니다.

    ![Agent Customizations 편집기 스크린샷, Instructions 탭과 새 지시사항 파일을 생성하는 드롭다운 표시](images/customization/create-instructions-file.png)

    또는, 명령 팔레트에서 **Chat: New Instructions File** 명령을 사용하세요(`kb(workbench.action.showCommands)`).

1. 위치를 선택하고 지시사항 파일의 파일 이름을 입력합니다. 이는 UI에서 사용되는 기본 이름입니다.

1. Markdown 형식을 사용하여 커스텀 지시사항을 작성합니다.

    * 파일 상단의 YAML 프런트매터를 채워 지시사항의 설명, 이름, 적용 시점을 구성합니다.
    * 파일 본문에 지시사항을 추가합니다.

Agent Customizations 편집기에서 기존 지시사항 파일을 열어 수정할 수 있습니다.

### AI로 지시사항 파일 생성하기

AI를 사용하여 목표가 명확한 지시사항 파일을 생성할 수 있습니다. 채팅에 `/create-instruction`을 입력하고 적용하고 싶은 관례나 가이드라인을 설명하세요(예: "이 프로젝트에서는 항상 탭과 단일 인용부호를 사용한다"). 에이전트가 명확화 질문을 한 후 적절한 `applyTo` 패턴과 내용을 가진 `.instructions.md` 파일을 생성합니다.

진행 중인 대화에서 지시사항을 추출할 수도 있습니다. 예를 들어, 채팅 세션 중 에이전트의 import 스타일을 수정했다면, "이 내용에서 지시사항을 추출해줘"라고 요청하여 해당 수정 사항을 프로젝트 관례로 캡처할 수 있습니다.

> [!NOTE]
> `/create-instruction`은 목표가 명확한 온디맨드 지시사항 파일을 생성합니다. 워크스페이스 전체의 상시 적용 지시사항을 생성하려면 [`/init` 명령](#generate-custom-instructions-for-your-workspace)을 사용하세요.

<details>
<summary>예시: 언어별 코딩 가이드라인</summary>

이 지시사항이 일반 코딩 가이드라인 파일을 참조하는 방식에 주목하세요. 지시사항을 여러 파일로 분리하여 정리하고 특정 주제에 초점을 맞출 수 있습니다.

```markdown
---
applyTo: "**/*.ts,**/*.tsx"
---
# TypeScript와 React에 대한 프로젝트 코딩 표준

모든 코드에 [일반 코딩 가이드라인](./general-coding.instructions.md)을 적용하세요.

## TypeScript 가이드라인
- 모든 새 코드에 TypeScript 사용
- 가능한 경우 함수형 프로그래밍 원칙을 따르기
- 데이터 구조와 타입 정의에는 interface 사용
- 불변 데이터(const, readonly) 선호
- optional chaining(?.) 및 nullish coalescing(??) 연산자 사용

## React 가이드라인
- 훅을 사용하는 함수형 컴포넌트 사용
- React 훅 규칙 준수(조건부 훅 사용 금지)
- children이 있는 컴포넌트에는 React.FC 타입 사용
- 컴포넌트를 작고 집중되게 유지
- 컴포넌트 스타일링에는 CSS 모듈 사용
```

</details>

<details>
<summary>예시: 문서 작성 가이드라인</summary>

문서 작성과 같은 비개발 활동을 포함하여 다양한 유형의 작업에 대한 지시사항 파일을 만들 수 있습니다.

```markdown
---
applyTo: "docs/**/*.md"
---
# 프로젝트 문서 작성 가이드라인

## 일반 가이드라인
- 명확하고 간결한 문서를 작성하세요.
- 일관된 용어와 스타일을 사용하세요.
- 해당되는 경우 코드 예제를 포함하세요.

## 문법
* 과거 시제(was, opened) 대신 현재 시제 동사(is, open)를 사용하세요.
* 사실에 기반한 문장과 직접적인 명령을 작성하세요. "could"나 "would" 같은 가정형 표현은 피하세요.
* 주체가 행동을 수행하는 능동태를 사용하세요.
* 독자에게 직접 말하듯 2인칭(you)으로 작성하세요.

## Markdown 가이드라인
- 콘텐츠를 정리하기 위해 제목을 사용하세요.
- 목록에는 글머리 기호를 사용하세요.
- 관련 리소스에 대한 링크를 포함하세요.
- 코드 스니펫에는 코드 블록을 사용하세요.
```

</details>

더 많은 커뮤니티 기여 예제는 [Awesome Copilot 리포지토리](https://github.com/github/awesome-copilot/tree/main)를 참고하세요.

## `AGENTS.md` 파일 사용하기

VS Code는 워크스페이스 루트에 있는 `AGENTS.md` Markdown 파일을 자동으로 감지하여 이 파일의 지시사항을 해당 워크스페이스의 모든 채팅 요청에 적용합니다. 이는 워크스페이스에서 여러 AI 에이전트를 사용하면서 모든 에이전트가 인식하는 단일 지시사항 세트를 원하거나, 모노레포의 특정 부분에 적용되는 하위 폴더 수준 지시사항을 원할 때 유용합니다.

`AGENTS.md`는 다음과 같은 경우에 사용하세요:

* 여러 AI 코딩 에이전트를 사용하면서 모든 에이전트가 인식하는 단일 지시사항 세트를 원하는 경우
* 모노레포의 특정 부분에 적용되는 하위 폴더 수준 지시사항을 원하는 경우

`AGENTS.md` 파일 지원을 활성화 또는 비활성화하려면 `setting(chat.useAgentsMdFile)` 설정을 구성하세요.

### 여러 `AGENTS.md` 파일 사용하기 (실험적)

하위 폴더에서 여러 `AGENTS.md` 파일을 사용하는 것은 프로젝트의 다른 부분에 다른 지시사항을 적용하고자 할 때 유용합니다. 예를 들어, 프론트엔드 코드용 `AGENTS.md` 파일 하나와 백엔드 코드용 파일 하나를 가질 수 있습니다.

워크스페이스에서 중첩된 `AGENTS.md` 파일 지원을 활성화 또는 비활성화하려면 실험적 설정인 `setting(chat.useNestedAgentsMdFiles)`를 사용하세요.

활성화하면, VS Code는 워크스페이스의 모든 하위 폴더에서 `AGENTS.md` 파일을 재귀적으로 검색하여 상대 경로를 채팅 컨텍스트에 추가합니다. 그러면 에이전트가 편집 중인 파일을 기준으로 어떤 지시사항을 사용할지 결정할 수 있습니다.

> [!TIP]
> 폴더별 지시사항을 위해, 폴더 구조와 일치하는 서로 다른 `applyTo` 패턴을 가진 여러 [`.instructions.md`](#use-instructionsmd-files) 파일을 사용할 수도 있습니다.

## `CLAUDE.md` 파일 사용하기

VS Code는 `CLAUDE.md` 파일을 자동으로 감지하여 `AGENTS.md`와 마찬가지로 상시 적용 지시사항으로 적용합니다. 이는 VS Code와 함께 Claude Code나 다른 Claude 기반 도구를 사용하면서 모두가 인식하는 단일 지시사항 세트를 원할 때 유용합니다.

VS Code는 다음 위치에서 `CLAUDE.md` 파일을 검색합니다:

| 위치 | 설명 |
|----------|-------------|
| 워크스페이스 루트 | 워크스페이스 루트의 `CLAUDE.md` |
| `.claude` 폴더 | 워크스페이스의 `.claude/CLAUDE.md` |
| 사용자 홈 | 모든 프로젝트에 대한 개인 지시사항을 위한 `~/.claude/CLAUDE.md` |
| 로컬 변형 | 로컬 전용 지시사항(버전 관리에 커밋되지 않음)을 위한 `CLAUDE.local.md` |

`CLAUDE.md` 파일 지원을 활성화 또는 비활성화하려면 `setting(chat.useClaudeMdFile)` 설정을 구성하세요.

> [!NOTE]
> `.claude/rules` 지시사항 파일의 경우, VS Code는 [Claude Rules 형식](https://code.claude.com/docs/en/memory#basic-structure)을 따라 glob 패턴에 `applyTo` 대신 `paths` 속성을 사용합니다. `paths` 속성은 glob 패턴의 배열을 받으며, 생략하면 기본값은 `**`(모든 파일)입니다.

## 워크스페이스를 위한 커스텀 지시사항 생성하기

VS Code는 워크스페이스를 분석하여 코딩 관행과 프로젝트 구조에 맞는 상시 적용 커스텀 지시사항을 생성할 수 있습니다. 이렇게 생성된 지시사항은 이후 워크스페이스의 모든 채팅 요청에 자동으로 적용됩니다.

지시사항을 생성할 때 VS Code는 다음 단계를 수행합니다:

1. 워크스페이스에 있는 `copilot-instructions.md`나 `AGENTS.md` 파일 같은 기존 AI 관례를 발견합니다.
1. 프로젝트 구조와 코딩 패턴을 분석합니다.
1. 프로젝트에 맞춘 포괄적인 워크스페이스 지시사항을 생성합니다.

워크스페이스를 위한 커스텀 지시사항을 생성하려면:

* 채팅 입력란에 `/init`을 입력하고 `kbstyle(Enter)`를 누르세요.

* `/create-instructions`를 입력한 후 생성하고 싶은 지시사항에 대한 설명을 입력하세요.

* Agent Customizations 편집기에서 드롭다운의 **Generate Instructions**를 선택하세요.

## 팀 간 커스텀 지시사항 공유하기

GitHub 조직 내 여러 워크스페이스와 리포지토리에서 커스텀 지시사항을 공유하려면 GitHub 조직 수준에서 정의할 수 있습니다.

VS Code는 사용자 계정이 액세스 권한을 가진 조직 수준에서 정의된 커스텀 지시사항을 자동으로 감지합니다. 이 지시사항들은 개인 및 워크스페이스 지시사항과 함께 **Chat Instructions** 메뉴에 표시되며, 모든 채팅 요청에 자동으로 적용됩니다.

조직 수준 커스텀 지시사항 검색을 활성화하려면 `setting(github.copilot.chat.organizationInstructions.enabled)`을 `true`로 설정하세요.

GitHub 문서에서 [조직을 위한 커스텀 지시사항 추가하기](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-organization-instructions)에 대해 알아보세요.

## 여러 기기 간 사용자 지시사항 파일 동기화하기

VS Code는 [Settings Sync](/docs/configure/settings-sync.md)를 사용해 여러 기기 간에 사용자 지시사항 파일을 동기화할 수 있습니다.

사용자 지시사항 파일을 동기화하려면, Settings Sync를 활성화하고 명령 팔레트에서 **Settings Sync: Configure**를 실행하세요(`kb(workbench.action.showCommands)`). 동기화할 설정 목록에서 **Prompts and Instructions**를 선택하세요.

## 설정에서 커스텀 지시사항 지정하기

> [!NOTE]
> 설정 기반 코드 생성 및 테스트 생성 지시사항은 VS Code 1.102부터 더 이상 지원되지 않습니다(deprecated). 대신 [파일 기반 지시사항](#types-of-instruction-files)을 사용하세요.

코드 리뷰, 커밋 메시지, 풀 리퀘스트 설명에 대해서는 여전히 VS Code 설정을 사용하여 커스텀 지시사항을 정의할 수 있습니다. 이 설정들은 `text` 속성(인라인 지시사항) 또는 `file` 속성(Markdown 파일 경로)을 가진 객체의 배열을 받습니다.

| 시나리오 | 설정 |
|----------|---------|
| 코드 리뷰 | `setting(github.copilot.chat.reviewSelection.instructions)` |
| 커밋 메시지 | `setting(github.copilot.chat.commitMessageGeneration.instructions)` |
| 풀 리퀘스트 설명 | `setting(github.copilot.chat.pullRequestDescriptionGeneration.instructions)` |

## 지시사항 우선순위

여러 유형의 커스텀 지시사항이 존재할 경우, 모두 AI에 제공됩니다. 충돌이 발생하면 우선순위가 높은 지시사항이 우선합니다:

1. 개인 지시사항(사용자 수준, 가장 높은 우선순위)
1. 리포지토리 지시사항(`.github/copilot-instructions.md` 또는 `AGENTS.md`)
1. 조직 지시사항(가장 낮은 우선순위)

## 효과적인 지시사항 작성을 위한 팁

* 지시사항을 짧고 자체 완결적으로 유지하세요. 각 지시사항은 단일하고 간단한 문장이어야 합니다. 여러 정보를 제공해야 한다면 여러 개의 지시사항으로 나누세요.

* 규칙의 이유를 포함하세요. 지시사항이 관례가 존재하는 _이유_를 설명하면 AI가 예외적인 상황에서 더 나은 판단을 내립니다. 예: "moment.js는 더 이상 유지보수되지 않고(deprecated) 번들 크기를 늘리기 때문에 `moment.js` 대신 `date-fns`를 사용하세요."

* 선호하는 패턴과 피해야 할 패턴을 구체적인 코드 예제와 함께 보여주세요. AI는 추상적인 규칙보다 예제에 더 효과적으로 반응합니다.

* 명확하지 않은 규칙에 집중하세요. 일반적인 린터나 포매터가 이미 강제하는 관례는 생략하세요.

* 작업별 또는 언어별 지시사항의 경우, 주제별로 여러 개의 `*.instructions.md` 파일을 사용하고 `applyTo` 속성으로 선택적으로 적용하세요.

* 프로젝트별 지시사항은 워크스페이스에 저장하여 다른 팀원과 공유하고 버전 관리에 포함시키세요.

* [프롬프트 파일](/docs/agent-customization/prompt-files.md)과 [커스텀 에이전트](/docs/agent-customization/custom-agents.md)에서 지시사항 파일을 재사용하고 참조하여 깔끔하고 집중력 있게 유지하고 지시사항 중복을 피하세요.

* 지시사항 사이의 공백은 무시되므로, 단일 단락, 별도의 줄, 또는 가독성을 위해 빈 줄로 구분하는 등 자유롭게 형식을 지정할 수 있습니다.

## 자주 묻는 질문

### 지시사항 파일이 적용되지 않는 이유는 무엇인가요?

> [!TIP]
> 채팅 커스터마이징 진단 보기를 사용하면 로드된 모든 지시사항 파일과 오류를 확인할 수 있습니다. Chat 보기에서 마우스 우클릭하고 **Diagnostics**를 선택하세요. [VS Code에서 AI 문제 해결하기](/docs/agents/agent-troubleshooting/troubleshooting.md)에 대해 자세히 알아보세요.

지시사항 파일이 적용되지 않는다면 다음을 확인하세요:

* 지시사항 파일이 올바른 위치에 있는지 확인하세요. `.github/copilot-instructions.md` 파일은 워크스페이스 루트의 `.github` 폴더에 있어야 합니다. `*.instructions.md` 파일은 `setting(chat.instructionsFilesLocations)` 설정에 지정된 폴더(또는 그 하위 디렉터리) 중 하나(기본값: `.github/instructions`)나 사용자 프로필에 있어야 합니다.

* `*.instructions.md` 파일의 경우, `applyTo` glob 패턴이 작업 중인 파일과 일치하는지 확인하세요. `applyTo` 속성이 지정되지 않으면 지시사항 파일이 자동으로 적용되지 않습니다. 채팅 응답의 **References** 섹션에서 어떤 지시사항 파일이 사용되었는지 확인하세요.

* 관련 설정이 활성화되어 있는지 확인하세요: 패턴 기반 지시사항의 경우 `setting(chat.includeApplyingInstructions)`, Markdown 링크로 참조된 지시사항의 경우 `setting(chat.includeReferencedInstructions)`, `AGENTS.md` 파일의 경우 `setting(chat.useAgentsMdFile)`.

고급 진단을 위해서는 [Chat Debug 보기에서 언어 모델 요청 확인하기](https://github.com/microsoft/vscode/wiki/Copilot-Issues#language-model-requests-and-responses) 또는 [applyTo 매칭 로직 디버깅하기](https://github.com/microsoft/vscode/wiki/Copilot-Issues#custom-instructions-logs)를 참고하세요.

### 커스텀 지시사항 파일이 어디서 왔는지 어떻게 알 수 있나요?

커스텀 지시사항 파일은 다양한 소스에서 올 수 있습니다: 내장(built-in), 사용자 프로필에서 사용자가 정의한 것, 현재 워크스페이스에서 정의된 워크스페이스 지시사항, 조직 수준 지시사항, 또는 확장 프로그램이 제공하는 지시사항.

커스텀 지시사항 파일의 소스를 확인하려면:

1. 명령 팔레트에서 **Chat: Configure Instructions**를 선택하세요(`kb(workbench.action.showCommands)`).
1. 목록에서 지시사항 파일에 마우스를 올리세요. 소스 위치가 툴팁에 표시됩니다.

채팅 커스터마이징 진단 보기를 사용하면 로드된 모든 지시사항 파일과 오류를 확인할 수 있습니다. Chat 보기에서 마우스 우클릭하고 **Diagnostics**를 선택하세요. [VS Code에서 AI 문제 해결하기](/docs/agents/agent-troubleshooting/troubleshooting.md)에 대해 자세히 알아보세요.

## 관련 리소스

* [Agent Skills 사용하기](/docs/agent-customization/agent-skills.md)
* [커스텀 에이전트 만들기](/docs/agent-customization/custom-agents.md)
* [커뮤니티가 기여한 지시사항, 프롬프트, 커스텀 에이전트](https://github.com/github/awesome-copilot)
</content>
