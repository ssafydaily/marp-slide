---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

# Destktop APP  설치

<div class="cols-6040">
<div>

- [`데스크톱 앱`](https://claude.ai/download) 다운로드 후 실행
- **Anthrophic 계정**으로 로그인
- 상단에 `Chat`, `Corwork`, `Code` 탭 확인

> - **Chat** : 질문, 문서초안 등 일반 대화. 
> - **Cowork** : 긴 작업을 여러개의 작은 작업으로 나누어 진행. 앱을 닫아도 계속 진행. (클라우드 VM 환경)
> - **Code** : 프로젝트 폴더의 파일을 읽고 수정. 코드 작성 요청. (로컬 파일 직접 접근)

</div>
<div>

![](images/00_desktop_app.png)

</div>
</div>

-----------------

# CLI 설치

- 터미널에서 `claude` 명령어로 **Claude**를 실행할 수 있도록 CLI 설치
```shell
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

- 설치 확인
```shell
claude --version
```
> 필요시 `path` 환경 변수에 등록
---------------

# 대화와 세션
- 대화 하기
<div class="cols">
<div>

```
# 대화형 세션 시작
claude

# 초기 프롬프트 넘기기
claude "프로젝트 구조를 설명해줘"
```

</div>
<div>

- 앱에서는 Code 탭을 선택하고 프로젝트 폴더를 지정하고 대화 시작

![](images/00_conversation.png)

</div>
</div>

---------------

# 세션 이어하기

<div class="cols">
<div>

- 마지막 대화 이어하기
```shell
claude --continue

# 또는
claude -c
```

- 특정 세션 이어하기
```shell
claude --continue <세션ID>

# 또는
claude -c <세션ID>
```

</div>
<div>

- 세션에 이름 붙이기
```shell
claude --name "프로젝트 구조 설명"

# 대화중에 
/reaname "프로젝트 구조 설명"
```

- 세션 목록 보기
```shell  
claude --sessions

# 또는
/resume
```

</div>
</div>

---------------

# 파일 참조(`@`)


<div class="cols">
<div>

- 대화 중에 `@파일명`으로 프로젝트 내 파일 참조 가능
- `@` 입력하면 프로젝트 내 파일 목록이 나타남

</div>
<div>

| 명령어 | 	역할  |
| ---- | -----|
| `/help` | 	도움말  |
| `/exit` | 	세션 종료  |
| `/model` | 	모델 변경 (Opus, Sonnet, Haiku)  |
| `/voice` | 	음성 입력 모드 (스페이스바 길게 눌러 녹음)  |
| `/resume` | 	이전 세션 목록에서 선택하여 재개  |
| `/rename` | 	현재 세션에 이름 붙이기  |
| `/clear` | 	대화 이력 초기화  |
| `/compact` | 	대화를 핵심만 남기고 압축  |

</div>
</div>

-------------------------

# 체크 포인트
- 파일이 수정되면 자동으로 체크 포인트 생성
- 결과가 마음에 들지 않으면 `Esc` 키를 두번 눌러 이전 체크 포인트로 되돌릴 수 있음

> **되감기 메뉴**
> - **Restore code and conversation** - 코드와 대화를 모두 해당 시점으로 되돌림
> - **Restore code** - 파일만 되돌리고 대화 맥락은 유지 (가장 자주 사용)
> - **Restore conversation** - 대화만 되돌리고 파일은 그대로
> - **Summarize from here** - 해당 시점부터 대화를 요약으로 압축
> - **Never mind** - 취소



<div class="callout tip">
  <div class="callout-title">
    TIP
  </div>

  - 체크포인트는 세션 종료 후에도 30일간 유지됩니다. 장기적인 버전 관리는 Git 커밋을 사용합니다
  - 되돌리기는 Claude가 수정한 파일에만 적용됩니다. 사용자가 직접 수정한 내용은 별도로 관리합니다  

</div>

-------------------------

# Model과 Effort 레벨

- `Claude Code`에서는 모델과 사고 깊이(`effort`)를 선택할 수 있다.
- `/model` 명령어로 모델 변경 가능

![h:300px](images/00_model.png)

- **Opus 4.8** : 복잡한 작업, 긴 문서, 코드 생성 (1M 토큰)
- **Sonnet 4.6** : 일상적인 작업
- **Haiku 4.5** : 빠른 응답, 간단한 질문, 짧은 문서

-------------------------

# Effort 레벨

- 모델의 사고 깊이(effort)를 조절하여 응답의 깊이와 창의성 조절 가능
  - **Low** : 빠른 응답, 간단한 작업
  - **Medium** : 균형 잡힌 사고 깊이와 응답 시간. 일반적인 코드 작성과 문서 작업에 적합
  - **High** : 깊이 있는 사고, 복잡한 문제 해결, 더 긴 응답 시간
  - **xxHigh** : 최대한의 사고 깊이, 매우 복잡한 문제 해결, 가장 긴 응답 시간
  - **max** : 모델이 허용하는 최대 사고 깊이, 가장 긴 응답 시간

- 명령어로 설정
```shell
/effort [low|medium|high|xxHigh|max|auto]
```

- `/model` 명령어로 모델 변경 시 Effort 레벨은 초기화되어 기본값인 `medium`으로 설정됩니다. 
-------------------------

- `/effort` 입력

![](images/00_effort.png)


<div class="callout info">
  <div class="callout-title">
 
  **ultrathink**
 
  </div>  

  - 한 번만 더 깊이 생각하게 하고 싶을 때는 메시지에 ultrathink를 포함
  - 문장 앞, 뒤, 중간 어디에 있어도 가능
  - 세션 effort 설정이 바뀌거나 API로 전송되는 effort 수준이 변경되는 것은 아님
  - "think", "think hard", "think more" 같은 문구는 키워드로 인식되지 않고 일반 텍스트로 처리됨
  
</div>

--------------------------
