#!/usr/bin/env node
/**
 * build.js — LangGraph-Course.html 빌드 스크립트
 *
 * 문제: Marp Core 는 --html 플래그에서도 <script> 태그를 HTML 이스케이프하며,
 *       슬라이드를 SVG <foreignObject> 안에 렌더하므로 슬라이드 내 스크립트는
 *       절대 실행되지 않는다.
 *
 * 해결: marp CLI 로 HTML 생성 → 이스케이프된 <script> 블록 제거 →
 *       Mermaid 초기화 스크립트를 <body> 레벨에 직접 주입.
 *
 * 사용법: node build.js
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR  = __dirname;
const MD   = path.join(DIR, 'LangGraph-Course.md');
const OUT  = path.join(DIR, 'LangGraph-Course.html');
const CSS  = path.join(DIR, 'theme/blueprint.css');

// 1) marp CLI 실행
// --theme-set 으로 CSS 를 테마셋에 등록 → blueprint.css 의 /* @theme blueprint */ 선언과
// front matter 의 'theme: blueprint' 가 이름으로 매칭되어 정상 적용됨
console.log('▶ marp CLI 실행 중…');
execSync('marp LangGraph-Course.md --theme-set theme/blueprint.css --html -o LangGraph-Course.html', {
  cwd: DIR,
  stdio: 'inherit',
});

// 2) 후처리
console.log('▶ Mermaid 스크립트 주입 중…');
let html = fs.readFileSync(OUT, 'utf8');

// 첫 번째 슬라이드에 남아있는 이스케이프된 <script>…</script> 블록 제거
html = html.replace(/&lt;script[\s\S]*?&lt;\/script&gt;/g, '');

// Mermaid 초기화 스크립트를 </body> 바로 앞에 주입
const MERMAID_SCRIPT = `
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: true,
  securityLevel: 'loose',
  theme: 'base',
  flowchart: { curve: 'basis', htmlLabels: true },
  themeVariables: {
    fontFamily: 'IBM Plex Mono, monospace', fontSize: '15px',
    primaryColor: '#ffffff', primaryBorderColor: '#3f5fc4', primaryTextColor: '#232a33',
    lineColor: '#8b94a3', secondaryColor: '#eef1fb', tertiaryColor: '#f7f8fa',
    clusterBkg: '#f7f8fa', clusterBorder: '#dce1e8', edgeLabelBackground: '#f7f8fa'
  }
});
</script>
`;

html = html.replace('</body>', MERMAID_SCRIPT + '</body>');

fs.writeFileSync(OUT, html, 'utf8');
console.log(`✓ 완료: ${OUT}`);
