---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

# Skills

- kills는 Claude의 기능을 확장하는 재사용 가능한 지시사항
- Anthropic 공식 스킬, 커뮤니티 스킬을 설치해서 바로 쓸 수도 있고, 직접 만들 수도 있다

## 번들 Skill 사용

- Claude Code에는 설치 없이 사용 가능한 내장된 번들 스킬이 있다
- `/code-review` - 최근 변경 파일을 3개 에이전트(재사용성, 품질, 효율성)가 병렬로 검토합니다
```
/code-review

# effort 수준이나 특정 부분에 집중
/code-review 에러 핸들링 위주로
```

-------------

- `/batch` - 대규모 변경을 병렬로 처리

```
/batch 모든 Python 파일의 print문을 logging으로 교체해줘
```
- 5-30개 단위로 분해하여 각각 git worktree에서 독립적으로 처리

- `/loop` - 프롬프트를 지정 간격으로 반복 실행합니다.
```
/loop 5m pytest를 실행하고 실패하면 알려줘
```

- `docx` : Word 문서 생성/편집 `pdf` : PDF 처리 `pptx` : 프레젠테이션 작성 `xlsx` : 스프레드시트 작업 
- `frontend-designUI/` : 웹 디자인 가이드

------------


## 공식 Skills 설치

- [Anthropic's implementation of skills for Claude](https://github.com/anthropics/skills)


| 스킬 | 	용도 |
| --- | ----- |
| webapp-testing | 	Playwright 기반 웹앱 자동 테스팅 |
| mcp-builder | 	MCP 서버 개발 가이드 (Phase 1-4 워크플로우) |
| claude-api | 	Anthropic SDK 레퍼런스 (코드에서 import 시 자동 활성화) |
| skill-creator | 	스킬 자체를 만드는 메타 스킬 |
| web-artifacts-builder | 	React + TypeScript 웹 아티팩트 생성 |

```sh
# 마켓플레이스를 등록하고 스킬을 설치합니다.
/plugin marketplace add anthropics/skills
# /plugin을 실행하면 플러그인 브라우저가 열립니다.
#  목록에서 원하는 스킬을 선택하여 설치.
/plugin
```

--------------------
## 커뮤니티 Skills

> 주요 마켓플레이스:

| 마켓플레이스 | 	규모 |	URL |
| ---------- | --- | ----- |
| SkillHub | 	7,000+ 스킬|	skillhub.club |
| ClawHub | 	3,200+ 스킬|	clawhub.ai |
| AgentSkills.to | 	프로덕션급 스킬|	agentskills.to |

- GitHub 저장소를 마켓플레이스로 등록하면 해당 저장소의 스킬을 설치할 수 있다.
```sh
/plugin marketplace add <github-owner>/<repo>
```

- 개발자에게 인기 있는 커뮤니티 스킬 패턴:
  - OWASP Security - OWASP Top 10 기반 보안 코드리뷰 체크리스트
  - Frontend Design - 디자인 시스템 로드, UI 컨벤션 강제
  - Webapp Testing - Playwright E2E 테스트 자동화

----------------------
# Create Skill

- 코드 리뷰 스킬 만들기
```
코드리뷰 스킬을 만들어줘.
`.claude/skills/review/SKILL.md` 파일로 만들어줘.
현재 변경사항(git diff)을 리뷰해서 버그, 보안, 성능, 컨벤션 위반을 찾고 심각도를 표시해줘.
```
> 사용법:
> ```
> /review
> /review 보안 취약점 위주로 확인해줘
> ```

----------------------

**작성 예시**


<div class="cols">
<div>

```markdown
---
name: review
description: 현재 변경사항을 코드리뷰합니다.
---
현재 변경사항(git diff)을 리뷰해:
1. 버그 가능성
2. 보안 취약점
3. 성능 문제
4. 코드 컨벤션 위반

각 항목별로 심각도(높음/중간/낮음)를 표시해.

$ARGUMENTS
```

</div>
<div>

- `name`은 `/review`로 호출할 이름
- `description`은 Claude가 자동 호출 여부를 판단할 때 사용
- `$ARGUMENTS`는 `/review 보안 위주로처럼` 뒤에 추가 지시를 붙일 때 치환

</div>
</div>

----------------

## 스킬 공유

- **프로젝트 스킬** (`.claude/skills/`) - 현재 프로젝트에서만 사용. 
  - Git에 커밋하면 팀원도 함께 사용합니다.

- **전역 스킬** (`~/.claude/skills/`) - 모든 프로젝트에서 사용. 
  - 개인 워크플로우에 맞는 스킬을 여기에 넣습니다.

- `/skills` 명령어로 현재 사용 가능한 스킬 목록을 확인할 수 있습니다.


-------------

## 주의 사항


<div class="callout tip">
  <div class="callout-title">
  
  TIP

  </div>

  - 배포, 메시지 전송 등 부작용이 있는 스킬에는 반드시 disable-model-invocation: true를 설정
  - `context: fork`를 설정한 스킬은 서브에이전트로 실행되어 메인 컨텍스트에 영향을 주지 않음
    - 분석이나 요약처럼 결과만 필요한 작업에 적합합니다.
  - !`command` 동적 컨텍스트는 스킬 로드 시 즉시 실행
    - 시간이 오래 걸리는 명령은 피합니다.
  - 스킬 디렉토리명이 곧 명령어 이름
    - `review/SKILL.md`는 `/review`로 호출
  - 내장 명령어(/clear, /exit, /init)와 이름이 겹치지 않도록 주의
  
</div>

