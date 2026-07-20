# LangGraph 풀코스 — Marp 슬라이드

상태 기반 LLM 에이전트를 LangGraph로 설계하는 6시간+ 풀코스입니다.
Marp(Markdown Presentation) 형식으로 작성되어, 마크다운을 그대로 PDF·PPTX·HTML로 내보낼 수 있습니다.

## 파일 구성

| 파일 | 설명 |
| --- | --- |
| `LangGraph-Course.md` | 강의 본체 (Marp 마크다운) |
| `theme/blueprint.css` | 커스텀 테마 — Blueprint(쿨 뉴트럴 + 모노스페이스) |
| `preview.html` | 이 환경에서 바로 보는 미리보기 (Marp + Mermaid 렌더) |

## 바로 보기

`preview.html` 을 열면 Mermaid 다이어그램까지 렌더된 전체 슬라이드를 볼 수 있습니다.

## 내보내기 (marp-cli)

> **주의**: Marp Core 는 `--html` 플래그에서도 `<script>` 태그를 HTML 이스케이프하며,
> 슬라이드가 SVG `<foreignObject>` 안에 들어가므로 슬라이드 내 스크립트가 실행되지 않습니다.
> HTML 내보내기는 반드시 `build.js` 를 사용하세요 — Mermaid 스크립트를 `<body>` 레벨에 자동 주입합니다.

```bash
npm i -g @marp-team/marp-cli

# HTML (Mermaid 다이어그램 포함) — build.js 사용 권장
node build.js

# PDF (Mermaid 포함 렌더)
marp LangGraph-Course.md --theme theme/blueprint.css --html --pdf --allow-local-files -o LangGraph-Course.pdf

# PPTX
marp LangGraph-Course.md --theme theme/blueprint.css --html --pptx -o LangGraph-Course.pptx
```

## VS Code Marp 확장 사용 시

- 슬라이드 레이아웃·테마는 그대로 미리보기에 나옵니다.
- **Mermaid 다이어그램은 VS Code 미리보기에서 렌더되지 않습니다** (확장이 스크립트를 실행하지 않기 때문).
  다이어그램을 보려면 위의 `marp --html` 내보내기 또는 `preview.html` 을 사용하세요.
- 설정에서 테마 경로를 등록하면 `theme: blueprint` 가 인식됩니다:
  `"markdown.marp.themes": ["./theme/blueprint.css"]`

## 편집 팁

- 슬라이드 구분은 `---` (3개 하이픈) 한 줄.
- 슬라이드별 지시문: `<!-- _class: section -->`, `<!-- _header: '...' -->`, `<!-- _paginate: false -->`.
- 코드는 ```` ```python ````, 다이어그램은 `<div class="mermaid"> ... </div>`.
- 색·여백·폰트는 `theme/blueprint.css` 상단의 `:root` 변수에서 일괄 조정.
