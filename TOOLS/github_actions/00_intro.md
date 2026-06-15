---
marp: true
theme: default
paginate: true
style: |
  @import "../../custom-theme.css"
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

<div class="cols-6040">
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


