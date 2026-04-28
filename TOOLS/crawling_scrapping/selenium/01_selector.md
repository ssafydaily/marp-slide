요소 선택자는 Selenium의 핵심입니다. 직접 조작해보면서 각 선택자의 차이를 익힐 수 있는 인터랙티브 도구를 먼저 보여드리겠습니다.탭을 전환하며 CSS / XPath / 기본 선택자를 각각 눌러보면 어느 HTML 요소가 매칭되는지 하이라이트로 확인할 수 있습니다.


---

## 1. 선택자 종류 총정리

```python
from selenium.webdriver.common.by import By

# ── 기본 선택자 ──────────────────────────────────────
driver.find_element(By.ID,               "board")
driver.find_element(By.CLASS_NAME,       "board-title")
driver.find_element(By.TAG_NAME,         "table")
driver.find_element(By.LINK_TEXT,        "다음")          # a 태그 텍스트 완전 일치
driver.find_element(By.PARTIAL_LINK_TEXT,"오늘")          # a 태그 텍스트 부분 일치
driver.find_element(By.NAME,             "q")             # form input의 name 속성

# ── CSS 선택자 (가장 범용적) ──────────────────────────
driver.find_element(By.CSS_SELECTOR,  "#board")                  # ID
driver.find_element(By.CSS_SELECTOR,  ".post-row")               # class
driver.find_element(By.CSS_SELECTOR,  "table.post-list")         # 태그+class 조합
driver.find_element(By.CSS_SELECTOR,  ".post-row .title a")      # 자손
driver.find_element(By.CSS_SELECTOR,  ".title > a")              # 직계 자식
driver.find_elements(By.CSS_SELECTOR, ".post-row")               # 복수 수집

# ── XPath (복잡한 조건에 강점) ────────────────────────
driver.find_element(By.XPATH, '//div[@id="board"]')
driver.find_element(By.XPATH, '//a[contains(text(), "매수")]')
driver.find_element(By.XPATH, '//tr[@class="post-row"][1]')      # 인덱스는 1부터!
driver.find_elements(By.XPATH,'//td[@class="author"]')
```

---

## 2. `find_element` vs `find_elements`

```python
# find_element  → 단일 요소, 없으면 NoSuchElementException 발생
title = driver.find_element(By.CSS_SELECTOR, ".board-title")
print(title.text)

# find_elements → 리스트 반환, 없으면 빈 리스트 [] (예외 없음)
rows = driver.find_elements(By.CSS_SELECTOR, ".post-row")
print(f"게시글 {len(rows)}개")

for row in rows:
    # 요소 안에서 다시 find_element — 범위를 좁혀서 탐색
    title = row.find_element(By.CSS_SELECTOR, ".title a")
    author = row.find_element(By.CSS_SELECTOR, ".author")
    date   = row.find_element(By.CSS_SELECTOR, ".date")
    print(title.text, "|", author.text, "|", date.text)
```

요소가 있는지 먼저 확인하고 싶을 때의 패턴:

```python
# 안전한 존재 확인
elements = driver.find_elements(By.CSS_SELECTOR, ".next-btn")
if elements:
    elements[0].click()
else:
    print("마지막 페이지")
```

---

## 3. 요소에서 데이터 추출

```python
element = driver.find_element(By.CSS_SELECTOR, ".post-row .title a")

# 텍스트 추출
print(element.text)                          # "오늘 실적 어떻게 보세요?"

# 속성 추출
print(element.get_attribute("href"))         # "https://...post/1024"
print(element.get_attribute("class"))        # 클래스명
print(element.get_attribute("innerHTML"))    # 내부 HTML 전체

# 상태 확인
print(element.is_displayed())   # 화면에 보이는지
print(element.is_enabled())     # 활성화되어 있는지
print(element.is_selected())    # 체크박스/라디오가 선택됐는지
```

---

## 4. CSS 선택자 실전 패턴

주식 커뮤니티 스크래핑에서 자주 쓰이는 패턴들입니다.

```python
# ── 특정 속성 값으로 선택 ─────────────────────────────
driver.find_element(By.CSS_SELECTOR, 'a[href="/post/1024"]')
driver.find_element(By.CSS_SELECTOR, 'input[type="search"]')

# ── n번째 자식 선택 ──────────────────────────────────
driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2)")     # 2번째 행
driver.find_element(By.CSS_SELECTOR, "td:first-child")      # 첫 번째 열
driver.find_element(By.CSS_SELECTOR, "td:last-child")       # 마지막 열

# ── 복수 클래스 ──────────────────────────────────────
driver.find_element(By.CSS_SELECTOR, ".post-row.active")    # 두 클래스 동시 보유

# ── 실전: 게시글 목록 전체 수집 ───────────────────────
rows = driver.find_elements(By.CSS_SELECTOR, "table.post-list tr.post-row")
data = []
for row in rows:
    data.append({
        "번호":  row.find_element(By.CSS_SELECTOR, "td.num").text,
        "제목":  row.find_element(By.CSS_SELECTOR, "td.title a").text,
        "작성자":row.find_element(By.CSS_SELECTOR, "td.author").text,
        "날짜":  row.find_element(By.CSS_SELECTOR, "td.date").text,
        "링크":  row.find_element(By.CSS_SELECTOR, "td.title a").get_attribute("href"),
    })
```

---

## 5. XPath 실전 패턴

CSS로 못 하는 것들을 XPath로 처리합니다. 가장 중요한 건 텍스트 내용으로 검색하는 것과 부모 역방향 탐색입니다.

```python
# ── 텍스트로 검색 (CSS는 불가, XPath만 가능) ─────────
driver.find_element(By.XPATH, '//a[text()="다음"]')                  # 정확히 일치
driver.find_element(By.XPATH, '//a[contains(text(), "매수")]')        # 포함

# ── 속성 조건 조합 ────────────────────────────────────
driver.find_element(By.XPATH, '//td[@class="title" and @data-id]')

# ── 인덱스로 특정 행 선택 (1부터 시작!) ──────────────
driver.find_element(By.XPATH, '(//tr[@class="post-row"])[1]')        # 첫 번째 행
driver.find_element(By.XPATH, '(//tr[@class="post-row"])[last()]')   # 마지막 행

# ── 부모·형제 역방향 탐색 (XPath만 가능) ─────────────
# "홍길동" 텍스트를 가진 td의 형제 td에서 날짜 꺼내기
driver.find_element(By.XPATH,
    '//td[text()="홍길동"]/following-sibling::td[@class="date"]'
)

# 특정 링크를 포함한 tr 행 전체 찾기
driver.find_element(By.XPATH,
    '//a[@href="/post/1024"]/ancestor::tr'
)

# ── 텍스트 normalize (앞뒤 공백 제거) ────────────────
driver.find_element(By.XPATH,
    '//a[normalize-space(text())="오늘 실적 어떻게 보세요?"]'
)
```

---

## 6. 선택자 선택 기준

| 상황 | 권장 선택자 | 이유 |
|------|------------|------|
| ID가 있음 | `By.ID` 또는 `By.CSS_SELECTOR "#id"` | 가장 빠르고 명확 |
| 여러 요소 수집 | `By.CSS_SELECTOR` | 간결하고 가독성 좋음 |
| 텍스트로 검색해야 함 | `By.XPATH` | CSS는 텍스트 검색 불가 |
| 부모/형제 요소 탐색 | `By.XPATH` | CSS는 역방향 탐색 불가 |
| `name` 속성 폼 요소 | `By.NAME` | 폼 입력 특화 |
| 링크 버튼 클릭 | `By.LINK_TEXT` | 직관적 |

실제 스크래핑 프로젝트에서는 CSS 선택자를 70%, XPath를 30% 정도 비율로 혼용하는 게 자연스럽습니다. CSS로 충분한데 굳이 XPath를 쓸 필요는 없고, 역방향 탐색이나 텍스트 검색이 필요한 순간에만 XPath를 꺼내면 됩니다.

다음 단계인 페이지 조작(클릭, 입력, 스크롤)이나 대기 전략에 대해 더 알고 싶으시면 알려주세요.