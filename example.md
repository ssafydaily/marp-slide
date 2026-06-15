---
marp: true
theme: marp-theme
paginate: true
---

<!-- _class: lead -->

# Marp Custom Theme
## 2컬럼 · 코드 · 콜아웃 · 테이블 예시
2026-06-15

---

## h2 — 슬라이드 메인 헤더

### h3 서브 섹션 제목

일반 본문 텍스트입니다. `인라인 코드`는 이렇게 표시됩니다.

#### h4 레이블 (작은 카테고리 표시)

- 리스트 아이템 1
- 리스트 아이템 2
- 리스트 아이템 3

---

## 2컬럼 레이아웃

<div class="cols">
<div class="col">

### 왼쪽 컬럼
일반 텍스트와 리스트를 나란히 배치할 수 있습니다.

- 항목 A
- 항목 B
- 항목 C

</div>
<div class="col">

### 오른쪽 컬럼

```python
def greet(name: str) -> str:
    """인사말을 반환합니다."""
    return f"Hello, {name}!"

print(greet("Marp"))
```

</div>
</div>

---

## 코드 블록

```javascript
// 비동기 데이터 페칭 예시
async function fetchData(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Fetch 실패:", err);
  }
}
```

---

## 콜아웃 — Info / Tip / Warning

<blockquote>

**ℹ️ Info**

기본 blockquote는 파란 Info 스타일로 표시됩니다.

</blockquote>

<blockquote class="tip">

**💡 Tip**

`class="tip"` 을 추가하면 녹색 Tip 스타일로 바뀝니다.

</blockquote>

<blockquote class="warning">

**⚠️ Warning**

`class="warning"` 을 추가하면 노란 Warning 스타일로 바뀝니다.

</blockquote>

---

## 테이블

| 항목 | 설명 | 타입 | 기본값 |
|------|------|------|--------|
| `theme` | 테마 이름 | string | `default` |
| `paginate` | 페이지 번호 표시 | boolean | `false` |
| `backgroundColor` | 배경 색상 | hex | `#ffffff` |
| `size` | 슬라이드 비율 | string | `16:9` |

---

## 40/60 비율 2컬럼

<div class="cols">
<div class="col col-40">

#### 설명
왼쪽을 좁게, 오른쪽을 넓게 쓰고 싶을 때 사용합니다.

- `col-40` + `col-60`
- `col-30` + `col-70`

</div>
<div class="col col-60">

```bash
# CLI 빌드 명령
marp --theme ./marp-theme.css \
     --html \
     --output ./dist \
     slide.md

# PDF 내보내기
marp --theme ./marp-theme.css \
     --pdf slide.md
```

</div>
</div>

---

## 카드 & 배지 유틸리티

<div class="cols">
<div class="col">

<div class="card">

**카드 컴포넌트**
`class="card"` 로 내용을 박스로 묶을 수 있습니다.

</div>

</div>
<div class="col">

버전 <span class="badge">v2.0</span> 에서 추가된 기능입니다.

<p class="small">작은 보조 텍스트는 class="small" 을 사용하세요.</p>

</div>
</div>
