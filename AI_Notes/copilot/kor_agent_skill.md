# VS Code에서 Agent Skills 사용하기

Agent Skills는 GitHub Copilot이 특정 작업을 수행할 때 관련성이 있다고 판단되면 불러오는 지침, 스크립트, 리소스 폴더입니다. Agent Skills는 [오픈 표준](https://agentskills.io)으로, GitHub Copilot for VS Code, GitHub Copilot CLI, GitHub Copilot 클라우드 에이전트 등 여러 AI 에이전트에서 동작합니다.

주로 코딩 가이드라인을 정의하는 [커스텀 인스트럭션](/docs/agent-customization/custom-instructions.md)과 달리, 스킬은 스크립트, 예제, 기타 리소스를 포함할 수 있는 특화된 기능과 워크플로를 제공합니다. 직접 만든 스킬은 이동 가능(portable)하며 스킬을 지원하는 모든 에이전트에서 동작합니다.

스킬과 다른 커스터마이징 옵션 간의 비교는 [커스터마이징 개념](/docs/agents/concepts/customization.md)을 참고하세요.

Agent Skills의 주요 이점:

* **Copilot 특화**: 컨텍스트를 반복해서 설명하지 않고도 도메인 특화 작업에 맞게 기능을 조정
* **반복 작업 감소**: 한 번 만들어두면 모든 대화에서 자동으로 사용
* **기능 조합**: 여러 스킬을 결합해 복잡한 워크플로 구성
* **효율적인 로딩**: 필요할 때만 관련 콘텐츠를 컨텍스트에 로드

> [!TIP]
> [Agent Customizations 편집기](/docs/agent-customization/overview.md#use-the-agent-customizations-editor) (프리뷰)를 사용하면 모든 에이전트 커스터마이징을 한 곳에서 찾아보고, 만들고, 관리할 수 있습니다. 명령 팔레트에서 **Chat: Open Customizations**를 실행하세요.

## Agent Skills와 커스텀 인스트럭션 비교

Agent Skills와 커스텀 인스트럭션은 모두 Copilot의 동작을 커스터마이징하는 데 도움을 주지만, 목적은 서로 다릅니다.

| 기능 | Agent Skills | 커스텀 인스트럭션 |
| ------- | ------------ | ------------------- |
| **목적** | 특화된 기능과 워크플로를 학습시킴 | 코딩 표준과 가이드라인을 정의 |
| **이동성** | VS Code, Copilot CLI, Copilot 클라우드 에이전트에서 동작 | VS Code와 GitHub.com에서만 동작 |
| **콘텐츠** | 지침, 스크립트, 예제, 리소스 | 지침만 |
| **범위** | 작업별로 필요 시 로드 | 항상 적용(또는 glob 패턴 기반) |
| **표준** | 오픈 표준 ([agentskills.io](https://agentskills.io)) | VS Code 전용 |

다음과 같은 경우 Agent Skills를 사용하세요:

* 여러 AI 도구에서 동작하는 재사용 가능한 기능을 만들고 싶을 때
* 지침과 함께 스크립트, 예제, 기타 리소스를 포함하고 싶을 때
* 더 넓은 AI 커뮤니티와 기능을 공유하고 싶을 때
* 테스트, 디버깅, 배포 프로세스 같은 특화된 워크플로를 정의하고 싶을 때

다음과 같은 경우 커스텀 인스트럭션을 사용하세요:

* 프로젝트별 코딩 표준을 정의하고 싶을 때
* 언어나 프레임워크 규칙을 설정하고 싶을 때
* 코드 리뷰나 커밋 메시지 가이드라인을 지정하고 싶을 때
* 파일 형식에 따라 glob 패턴 기반 규칙을 적용하고 싶을 때

## 스킬 만들기

> [!TIP]
> 채팅 입력창에 `/skills`를 입력하면 **Configure Skills** 메뉴를 빠르게 열 수 있습니다.

스킬은 동작을 정의하는 `SKILL.md` 파일이 있는 디렉터리에 저장됩니다. VS Code는 두 가지 유형의 스킬을 지원합니다.

| 스킬 유형 | 위치 |
| ---------- | -------- |
| 저장소에 저장되는 프로젝트 스킬 | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| 사용자 프로필에 저장되는 개인 스킬 | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |

`setting(chat.agentSkillsLocations)` 설정을 사용하면 프로젝트 스킬을 위한 추가 파일 위치를 구성할 수 있습니다. 다른 폴더 구조로 스킬을 정리하거나 여러 스킬 디렉터리를 두고 싶을 때 유용합니다.

> [!TIP]
> 모노레포에서는 `setting(chat.useCustomizationsInParentRepositories)`를 활성화하면 상위 저장소 루트에서 스킬을 찾을 수 있습니다. 자세한 내용은 [상위 저장소 탐색](/docs/agent-customization/overview.md#use-customizations-in-a-monorepo)을 참고하세요.

스킬을 만드는 방법:

1. Chat 뷰에서 **Configure Chat**(톱니바퀴 아이콘)을 선택해 Agent Customizations 편집기를 열고, **Skills** 탭을 선택합니다.

1. 드롭다운에서 **New Skill (Workspace)** 또는 **New Skill (User)**를 선택해 저장 위치를 정합니다.

    ![Agent Customizations 편집기의 Skills 탭과 새 스킬 생성 드롭다운을 보여주는 스크린샷](images/customization/create-skill-v2.png)

1. 위치를 선택하고 스킬 이름을 입력합니다.

1. `SKILL.md` 파일의 YAML 프런트매터를 채우고 본문에 지침을 작성합니다.

    ```markdown
    ---
    name: skill-name
    description: 스킬이 무엇을 하는지, 언제 사용하는지에 대한 설명
    ---

    # Skill Instructions

    상세한 지침, 가이드라인, 예제를 여기에 작성합니다...
    ```

1. 필요하다면 스킬 디렉터리에 스크립트, 예제, 기타 리소스를 추가합니다.

    예를 들어 웹 애플리케이션 테스트용 스킬은 다음과 같은 구성을 가질 수 있습니다.

    * `SKILL.md` - 테스트 실행 지침
    * `test-template.js` - 테스트 파일 템플릿
    * `examples/` - 테스트 시나리오 예제

    > [!NOTE]
    > 추가 파일이 에이전트에 인식되려면 반드시 `SKILL.md`에서 참조해야 합니다. `[test template](./test-template.js)`처럼 상대 경로를 사용한 마크다운 링크 문법을 사용하세요.

### AI로 스킬 생성하기

원하는 기능을 설명하면 AI가 스킬을 생성해줄 수 있습니다. 채팅에 `/create-skill`을 입력하고 원하는 스킬을 설명하세요(예: "통합 테스트를 실행하고 디버깅하는 스킬"). 에이전트가 명확화를 위한 질문을 한 뒤 디렉터리 구조, 지침, 프런트매터가 포함된 `SKILL.md` 파일을 생성합니다.

진행 중인 대화에서 재사용 가능한 스킬을 추출할 수도 있습니다. 예를 들어 복잡한 이슈를 여러 차례에 걸쳐 디버깅한 세션 후 "방금 우리가 디버깅한 방식으로 스킬을 만들어줘"라고 요청하면 다단계 절차를 재사용 가능한 스킬로 캡처할 수 있습니다.

Agent Customizations 편집기의 드롭다운에서 **Generate Skill**을 선택해도 스킬을 생성할 수 있습니다.

## SKILL.md 파일 형식

`SKILL.md` 파일은 스킬의 메타데이터와 동작을 정의하는 YAML 프런트매터가 포함된 마크다운 파일입니다.

### 헤더(필수)

헤더는 다음 필드들로 구성된 YAML 프런트매터로 작성됩니다.

| 필드 | 필수 여부 | 설명 |
|-------|----------|-------------|
| `name` | 예 | 스킬의 고유 식별자. 소문자, 숫자, 하이픈만 허용됩니다(예: `webapp-testing`). 슬래시, 콜론, 점, 네임스페이스 접두사는 사용할 수 없습니다. 상위 디렉터리 이름과 일치해야 합니다. 최대 64자. 잘못된 문자가 포함된 이름은 스킬이 조용히 로드되지 않게 됩니다. |
| `description` | 예 | 스킬이 무엇을 하는지, **언제 사용하는지**에 대한 설명. Copilot이 스킬 로드 여부를 판단하는 데 도움이 되도록 기능과 사용 사례를 구체적으로 작성하세요. 최대 1024자. |
| `argument-hint` | 아니오 | 스킬이 슬래시 명령으로 호출될 때 채팅 입력창에 표시되는 힌트 텍스트. 사용자가 어떤 추가 정보를 제공해야 하는지 이해하도록 돕습니다(예: `[test file] [options]`). |
| `user-invocable` | 아니오 | 스킬이 채팅 메뉴에서 슬래시 명령으로 표시될지 여부를 제어합니다. 기본값은 `true`입니다. `/` 메뉴에서 스킬을 숨기되 에이전트가 자동으로 로드할 수 있게 하려면 `false`로 설정하세요. |
| `disable-model-invocation` | 아니오 | 에이전트가 관련성에 따라 스킬을 자동으로 로드할 수 있는지 여부를 제어합니다. 기본값은 `false`입니다. `/` 슬래시 명령을 통한 수동 호출만 허용하려면 `true`로 설정하세요. |
| `context` | 아니오 | (실험적) 스킬이 로드되는 방식을 제어합니다. 기본값은 인라인(스킬 지침이 부모 에이전트의 컨텍스트에 추가됨)입니다. 전용 서브에이전트 컨텍스트에서 실행하려면 `fork`로 설정하세요. [포크된 컨텍스트에서 스킬 실행](#run-a-skill-in-a-forked-context-experimental) 참고. |

> [!IMPORTANT]
> 스킬이 [플러그인](/docs/agent-customization/agent-plugins.md)을 통해 배포되는 경우 플러그인 이름이 자동으로 명령 접두사로 사용됩니다(예: `/my-plugin:test-runner`). `name` 필드에 네임스페이스 접두사를 수동으로 추가하지 마세요. `myorg/skillname`이나 `myorg:skillname` 같은 접두사를 사용하면 스킬이 조용히 로드되지 않게 됩니다.

### 본문

스킬 본문에는 Copilot이 이 스킬을 사용할 때 따라야 할 지침, 가이드라인, 예제가 포함됩니다. 다음 내용을 설명하는 명확하고 구체적인 지침을 작성하세요.

* 스킬이 달성하는 것
* 스킬을 사용해야 하는 시점
* 따라야 할 단계별 절차
* 예상되는 입력과 출력의 예
* 포함된 스크립트나 리소스에 대한 참조

스킬 디렉터리 내 파일은 상대 경로로 참조할 수 있습니다. 예를 들어 스킬 디렉터리의 스크립트를 참조하려면 `[test script](./test-template.js)`를 사용하세요.

### 포크된 컨텍스트에서 스킬 실행(실험적)

기본적으로 VS Code가 스킬을 로드하면 스킬의 지침이 부모 에이전트의 컨텍스트 윈도우에 추가됩니다. 규모가 큰 스킬이나, 중간 추론 과정이 나머지 대화와 관련이 없는 스킬의 경우 **포크된 컨텍스트**에서 실행할 수 있습니다. 포크된 컨텍스트에서는 스킬이 전용 서브에이전트에서 실행되며 최종 결과만 부모 에이전트로 반환됩니다. 이를 통해 메인 대화의 컨텍스트를 깔끔하게 유지할 수 있습니다.

포크된 컨텍스트에서 스킬을 실행하려면 `SKILL.md` 프런트매터의 `context` 필드를 `fork`로 설정하세요.

```markdown
---
name: review-pr
description: 코드 품질, 스타일, 정확성을 위해 풀 리퀘스트를 리뷰합니다. PR 리뷰를 요청받았을 때 사용하세요.
context: fork
---

# PR review

풀 리퀘스트를 리뷰하기 위해 다음 단계를 따르세요...
```

다음과 같은 스킬에는 `context: fork`를 사용하세요.

* 많은 파일을 읽거나 긴 조사를 수행하지만 그 세부 내용이 메인 대화에 남을 필요가 없는 스킬
* 부모 에이전트가 직접 활용할 수 있는 집중된 결과(요약, 보고서, 소규모 편집 등)를 만들어내는 스킬
* 최종 출력 외에는 부모 에이전트의 동작에 영향을 주지 않아야 하는 스킬

> [!NOTE]
> 포크된 컨텍스트에서 스킬을 실행하는 기능은 실험적입니다. 이 기능을 사용하려면 VS Code에서 `setting(github.copilot.chat.skillTool.enabled)` 설정을 활성화하세요.

## 스킬 예제

다음은 만들 수 있는 다양한 유형의 스킬 예제입니다.

<details>
<summary>예제: 웹 애플리케이션 테스트 스킬</summary>

````markdown
---
name: webapp-testing
description: Playwright를 사용해 웹 애플리케이션을 테스트하는 가이드입니다. 브라우저 기반 테스트를 만들거나 실행하라는 요청을 받았을 때 사용하세요.
---

# Web Application Testing with Playwright

이 스킬은 Playwright를 사용해 웹 애플리케이션의 브라우저 기반 테스트를 만들고 실행하는 데 도움을 줍니다.

## When to use this skill

다음이 필요할 때 이 스킬을 사용하세요:
- 웹 애플리케이션을 위한 새로운 Playwright 테스트 작성
- 실패하는 브라우저 테스트 디버깅
- 새 프로젝트를 위한 테스트 인프라 구성

## Creating tests

1. [테스트 템플릿](./test-template.js)에서 표준 테스트 구조를 확인하세요
2. 테스트할 사용자 플로를 식별하세요
3. `tests/` 디렉터리에 새 테스트 파일을 만드세요
4. Playwright의 로케이터를 사용해 요소를 찾으세요(역할 기반 셀렉터 권장)
5. 예상 동작을 검증하는 assertion을 추가하세요

## Running tests

로컬에서 테스트를 실행하려면:
```bash
npx playwright test
```

테스트를 디버그하려면:
```bash
npx playwright test --debug
```

## Best practices

- 동적 콘텐츠에는 data-testid 속성을 사용하세요
- 테스트는 독립적이고 원자적으로 유지하세요
- 복잡한 페이지에는 Page Object Model을 사용하세요
- 실패 시 스크린샷을 찍으세요
````

</details>

<details>
<summary>예제: GitHub Actions 디버깅 스킬</summary>

````markdown
---
name: github-actions-debugging
description: 실패하는 GitHub Actions 워크플로를 디버깅하는 가이드입니다. 실패하는 GitHub Actions 워크플로를 디버깅하라는 요청을 받았을 때 사용하세요.
---

# GitHub Actions Debugging

이 스킬은 풀 리퀘스트에서 실패하는 GitHub Actions 워크플로를 디버깅하는 데 도움을 줍니다.

## Process

1. `list_workflow_runs` 도구를 사용해 풀 리퀘스트의 최근 워크플로 실행과 상태를 조회하세요
2. `summarize_job_log_failures` 도구를 사용해 실패한 작업의 로그에 대한 AI 요약을 받으세요
3. 더 많은 정보가 필요하면 `get_job_logs` 또는 `get_workflow_run_logs` 도구를 사용해 전체 실패 로그를 확인하세요
4. 로컬 환경에서 실패를 재현해보세요
5. 실패한 빌드를 수정하고 커밋하기 전에 수정 사항을 검증하세요

## Common issues

- **누락된 환경 변수**: 필요한 모든 시크릿이 구성되어 있는지 확인하세요
- **버전 불일치**: 액션 버전과 의존성이 호환되는지 확인하세요
- **권한 문제**: 워크플로가 필요한 권한을 가지고 있는지 확인하세요
- **타임아웃 문제**: 긴 작업을 분할하거나 타임아웃 값을 늘리는 것을 고려하세요
````

</details>

## 슬래시 명령으로 스킬 사용하기

스킬은 [프롬프트 파일](/docs/agent-customization/prompt-files.md)과 함께 채팅에서 슬래시 명령으로 사용할 수 있습니다. 채팅 입력창에 `/`를 입력하면 사용 가능한 스킬과 프롬프트 목록이 표시되며, 스킬을 선택해 호출할 수 있습니다.

슬래시 명령 뒤에 추가 컨텍스트를 덧붙일 수도 있습니다. 예를 들어 `/webapp-testing for the login page` 또는 `/github-actions-debugging PR #42`처럼 사용합니다.

기본적으로 모든 스킬은 `/` 메뉴에 표시됩니다. `user-invocable`과 `disable-model-invocation` 프런트매터 속성을 사용해 각 스킬에 접근하는 방식을 제어할 수 있습니다.

| 구성 | 슬래시 명령 | Copilot이 자동 로드 | 사용 사례 |
|---|---|---|---|
| 기본값(두 속성 모두 생략) | 가능 | 가능 | 범용 스킬 |
| `user-invocable: false` | 불가능 | 가능 | 모델이 관련성이 있을 때 로드하는 백그라운드 지식 스킬 |
| `disable-model-invocation: true` | 가능 | 불가능 | 필요할 때만 직접 실행하고 싶은 스킬 |
| 둘 다 설정 | 불가능 | 불가능 | 비활성화된 스킬 |

## Copilot이 스킬을 사용하는 방식

스킬은 컨텍스트를 효율적으로 유지하기 위해 콘텐츠를 점진적으로 로드합니다. 다음은 Copilot이 `webapp-testing` 스킬을 사용하는 방식의 예입니다.

1. **탐색(Discovery)**: Copilot은 YAML 프런트매터에서 스킬의 `name`과 `description`을 읽습니다. "로그인 페이지 테스트를 도와줘"라고 요청하면 Copilot은 이를 설명을 기반으로 `webapp-testing` 스킬과 매칭합니다.

2. **지침 로딩(Instructions loading)**: Copilot은 `SKILL.md` 본문을 컨텍스트에 로드해 상세한 테스트 절차와 가이드라인에 접근합니다. 채팅에 `/webapp-testing`을 입력해 이 단계를 직접 트리거할 수도 있습니다.

3. **리소스 접근(Resource access)**: Copilot이 지침을 따라 작업을 진행하면서 `test-template.js`나 예제 시나리오 같은 스킬 디렉터리의 추가 파일에 필요할 때만 접근합니다. 지침에서 참조되지 않은 파일은 로드되지 않습니다.

이 3단계 로딩 시스템을 통해 컨텍스트를 많이 소비하지 않고도 많은 스킬을 설치할 수 있습니다. Copilot은 각 작업에 관련된 것만 로드합니다.

[포크된 컨텍스트](#run-a-skill-in-a-forked-context-experimental)를 선택한 스킬도 동일한 탐색 단계를 거치지만, 지침과 읽어들이는 파일은 별도의 서브에이전트에 로드됩니다. 최종 결과만 부모 에이전트로 반환됩니다.

## 공유 스킬 사용하기

다른 사람이 만든 스킬을 사용해 Copilot의 기능을 확장할 수 있습니다. [github/awesome-copilot](https://github.com/github/awesome-copilot) 저장소에는 점점 늘어나는 커뮤니티의 스킬, 커스텀 에이전트, 인스트럭션, 프롬프트 모음이 있습니다. [anthropics/skills](https://github.com/anthropics/skills) 저장소에는 추가 참고용 스킬이 있습니다.

[에이전트 플러그인](/docs/agent-customization/agent-plugins.md)에 포함된 스킬을 찾아 설치할 수도 있습니다. 설치된 플러그인의 스킬은 **Configure Skills** 메뉴에서 로컬에 정의된 스킬과 함께 표시됩니다.

공유 스킬을 사용하는 방법:

1. 저장소에서 사용 가능한 스킬을 살펴보세요
1. 스킬 디렉터리를 `.github/skills/` 폴더로 복사하세요
1. 필요에 맞게 `SKILL.md` 파일을 검토하고 수정하세요
1. 필요하다면 리소스를 수정하거나 추가하세요

> [!TIP]
> 요구 사항과 보안 표준을 충족하는지 확인하기 위해 공유 스킬을 사용하기 전에 항상 검토하세요. VS Code의 [터미널 도구](/docs/chat/chat-tools.md#run-terminal-commands)는 스크립트 실행을 제어할 수 있는 기능을 제공하며, 구성 가능한 허용 목록과 자동 승인 옵션을 포함한 엄격한 제어가 가능합니다([자동 승인 옵션](/docs/agents/approvals.md#automatically-approve-terminal-commands)). 자동 승인 기능의 [보안 고려사항](/docs/agents/security.md#approvals-and-review)도 참고하세요.

## 확장 프로그램에서 스킬 기여하기

확장 프로그램은 `package.json`의 `chatSkills` 기여 지점을 사용해 스킬을 제공할 수 있습니다. 경로는 [Agent Skills 사양](https://agentskills.io/specification)을 따르는 `SKILL.md` 파일이 있는 디렉터리를 가리켜야 합니다.

### 필수 폴더 구조

스킬 디렉터리는 다음 구조를 따라야 합니다.

```text
extension-root/
└── skills/
    └── my-skill/           # 디렉터리 이름은 SKILL.md의 `name` 필드와 일치해야 함
        └── SKILL.md         # 필수
```

### package.json에 스킬 등록하기

확장 프로그램의 `package.json`에 `chatSkills` 기여 지점을 추가하세요. `path` 속성은 해당하는 `SKILL.md` 파일을 가리켜야 합니다.

```json
{
  "contributes": {
    "chatSkills": [
      {
        "path": "./skills/my-skill/SKILL.md"
      }
    ]
  }
}
```

> [!IMPORTANT]
> `SKILL.md` 프런트매터의 `name` 필드는 상위 디렉터리 이름과 일치해야 합니다. 예를 들어 디렉터리가 `skills/my-skill/`이라면 `name` 필드는 `my-skill`이어야 합니다. 이름이 일치하지 않으면 스킬이 로드되지 않습니다.

`SKILL.md` 파일은 [프로젝트 및 개인 스킬](#create-a-skill)과 동일한 형식을 따릅니다. 예시:

```markdown
---
name: my-skill
description: 스킬이 무엇을 하는지, 언제 사용하는지에 대한 설명.
---

# My Skill

스킬에 대한 상세 지침...
```

## Agent Skills 표준

Agent Skills는 다양한 AI 에이전트 간의 이동성을 가능하게 하는 오픈 표준입니다. VS Code에서 만든 스킬은 다음을 포함한 여러 에이전트에서 동작합니다.

* **VS Code의 GitHub Copilot**: 채팅 및 에이전트 모드에서 사용 가능
* **GitHub Copilot CLI**: 터미널 작업 시 접근 가능
* **GitHub Copilot 클라우드 에이전트**: 자동화된 코딩 작업 중 사용됨

Agent Skills 표준에 대해 더 알아보려면 [agentskills.io](https://agentskills.io)를 참고하세요.

## 관련 자료

* [AI 응답 커스터마이징 개요](/docs/agent-customization/overview.md)
* [커스텀 인스트럭션 만들기](/docs/agent-customization/custom-instructions.md)
* [재사용 가능한 프롬프트 파일 만들기](/docs/agent-customization/prompt-files.md)
* [커스텀 에이전트 만들기](/docs/agent-customization/custom-agents.md)
* [Agent Skills 사양](https://agentskills.io)
* [참고 스킬 저장소](https://github.com/anthropics/skills)
* [에이전트 플러그인 찾아보고 관리하기](/docs/agent-customization/agent-plugins.md)
