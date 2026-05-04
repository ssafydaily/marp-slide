각 탭의 "시뮬레이션 실행" 버튼을 눌러보면 세 전략이 시간상으로 어떻게 다르게 동작하는지 확인할 수 있습니다. 이제 전체 내용을 코드와 함께 정리해드리겠습니다.

---

## 1. 세 가지 대기 전략 비교

| | `time.sleep` | Implicit Wait | Explicit Wait |
|---|---|---|---|
| 설정 위치 | 코드 곳곳 | 드라이버 생성 직후 1회 | 필요한 곳마다 |
| 대기 조건 | 없음 (무조건) | DOM 존재 여부만 | 다양한 조건 선택 가능 |
| 요소 발견 시 | 남은 시간도 대기 | 즉시 반환 | 즉시 반환 |
| 타임아웃 시 | 없음 | `NoSuchElementException` | `TimeoutException` |
| 권장 여부 | 비권장 | 보조적으로만 | **권장** |

---

## 2. `time.sleep` — 쓰면 안 되는 이유

```python
import time

driver.find_element(By.CSS_SELECTOR, ".next-btn").click()
time.sleep(3)   # 무조건 3초 — 서버가 1초 만에 응답해도 2초 낭비

posts = driver.find_elements(By.CSS_SELECTOR, ".post-item")
```

유일하게 허용되는 사용 패턴은 **서버 부하 방지**를 위한 페이지 간 최소 간격뿐입니다.

```python
# 페이지네이션 루프에서 서버 과부하 방지용으로만 허용
for page in range(1, 11):
    scrape_page()
    time.sleep(0.5)   # 서버 배려 — 이 용도에 한해서만 사용
```

---

## 3. Implicit Wait — 전역 폴링 대기

```python
from selenium import webdriver

driver = webdriver.Chrome(...)
driver.implicitly_wait(10)  # 드라이버 생성 직후 딱 한 번만 설정

# 이후 모든 find_element에 자동 적용
# 500ms 간격으로 DOM을 폴링하다가 요소가 나타나면 즉시 반환
element = driver.find_element(By.CSS_SELECTOR, ".post-item")
```

**함정 — `find_elements`와 함께 쓰면 작동 안 함:**

```python
driver.implicitly_wait(10)

# find_elements는 요소가 없어도 빈 리스트를 즉시 반환해버림
# → implicit wait이 전혀 적용되지 않음
rows = driver.find_elements(By.CSS_SELECTOR, ".post-row")
if not rows:
    print("비어있음")  # 로딩 중일 수도 있는데 바로 빈 리스트 반환
```

---

## 4. Explicit Wait + Expected Conditions — 실전 권장 방식

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)   # 최대 10초, 500ms 간격 폴링

# 기본 사용 패턴
element = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, ".post-item")
))
```

### Expected Conditions 전체 목록

실전에서 자주 쓰는 EC들을 상황별로 정리했습니다.

```python
# ── 존재 / 가시성 ─────────────────────────────────────────
# DOM에 추가됐는지 (숨겨진 요소도 통과)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".post-list")))

# 화면에 실제로 보이는지 (display:none이면 대기)
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-done")))

# 요소가 사라질 때까지 대기 (로딩 스피너 사라지는 시점 포착)
wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".spinner")))

# ── 클릭 가능 여부 ────────────────────────────────────────
# 버튼이 활성화(enabled)되고 화면에 보일 때까지
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".next-btn")))

# ── 텍스트 조건 ──────────────────────────────────────────
# 특정 요소 안에 원하는 텍스트가 포함될 때까지
wait.until(EC.text_to_be_present_in_element(
    (By.CSS_SELECTOR, ".status"), "로드 완료"
))

# ── 복수 요소 ─────────────────────────────────────────────
# 여러 요소가 모두 로드될 때까지 (반환값이 리스트)
posts = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, ".post-row")
))

# ── URL / 제목 변화 ──────────────────────────────────────
# 페이지 이동 완료 확인
wait.until(EC.url_contains("page=2"))
wait.until(EC.title_contains("삼성전자"))

# ── Alert 팝업 ───────────────────────────────────────────
wait.until(EC.alert_is_present())

# ── 프레임 ───────────────────────────────────────────────
wait.until(EC.frame_to_be_available_and_switch_to_it("frame_id"))
```

---

## 5. 커스텀 조건 — EC로 해결 안 될 때

EC에 없는 조건은 람다 또는 클래스로 직접 만들 수 있습니다.

```python
# 람다로 간단한 커스텀 조건
# — 리스트 아이템이 5개 이상 로드될 때까지
posts = wait.until(
    lambda d: d.find_elements(By.CSS_SELECTOR, ".post-row")
    if len(d.find_elements(By.CSS_SELECTOR, ".post-row")) >= 5
    else False
)

# — 페이지 JS 로딩 완전 완료 확인
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

# — 특정 속성 값이 바뀔 때까지
wait.until(lambda d:
    d.find_element(By.ID, "status").get_attribute("data-loaded") == "true"
)

# 클래스로 재사용 가능한 커스텀 조건 만들기
class minimum_elements:
    def __init__(self, locator, count):
        self.locator = locator
        self.count = count

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        return elements if len(elements) >= self.count else False

# 사용
posts = wait.until(minimum_elements((By.CSS_SELECTOR, ".post-row"), 5))
```

---

## 6. 동적 콘텐츠 처리 패턴

### 무한 스크롤 페이지

```python
import time

def collect_infinite_scroll(driver, max_items=100):
    wait = WebDriverWait(driver, 10)
    collected = set()

    while len(collected) < max_items:
        # 현재 로드된 항목 수집
        items = driver.find_elements(By.CSS_SELECTOR, ".post-item")
        for item in items:
            collected.add(item.text.strip())

        prev_count = len(items)

        # 맨 아래로 스크롤 → 새 콘텐츠 로드 트리거
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # 새 항목이 로드될 때까지 대기 (이전보다 많아질 때)
        try:
            wait.until(lambda d:
                len(d.find_elements(By.CSS_SELECTOR, ".post-item")) > prev_count
            )
        except TimeoutException:
            print("더 이상 콘텐츠 없음 — 수집 종료")
            break

        time.sleep(0.3)   # 서버 부하 방지

    return list(collected)
```

### 로딩 스피너 대기

```python
from selenium.common.exceptions import TimeoutException

def wait_for_content_load(driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    try:
        # 1. 스피너가 나타날 때까지 잠깐 기다림 (없을 수도 있음)
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
        )
        # 2. 스피너가 사라질 때까지 대기
        wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
        )
    except TimeoutException:
        pass  # 스피너 없는 페이지면 그냥 통과

    # 3. 실제 콘텐츠 확인
    return wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".post-row"))
    )
```

### `StaleElementReferenceException` 방어 패턴

페이지가 부분 새로고침되면 이미 찾아둔 요소 레퍼런스가 무효화됩니다.

```python
from selenium.common.exceptions import StaleElementReferenceException

def safe_get_text(driver, locator, retries=3):
    """요소가 stale해지면 다시 찾아서 재시도"""
    for attempt in range(retries):
        try:
            element = driver.find_element(*locator)
            return element.text
        except StaleElementReferenceException:
            if attempt == retries - 1:
                raise
            time.sleep(0.3)

# 사용
title = safe_get_text(driver, (By.CSS_SELECTOR, ".post-title"))
```

---

## 7. 실전 종합 패턴 — 게시글 수집기

지금까지 배운 대기 전략을 전부 녹인 실전 코드입니다.

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

class StockBoardScraper:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def go_to_board(self, stock_code):
        self.driver.get(
            f"https://finance.naver.com/item/board.naver?code={stock_code}"
        )
        # 쿠키 팝업이 있으면 닫기
        try:
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_agree"))
            )
            btn.click()
        except TimeoutException:
            pass

    def collect_page(self):
        # 로딩 스피너 사라질 때까지 대기
        try:
            self.wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".loading")
            ))
        except TimeoutException:
            pass

        # 게시글 행이 최소 1개 이상 로드될 때까지 대기
        rows = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "table.type2 tr")
            )
        )

        results = []
        for row in rows:
            try:
                a    = row.find_element(By.CSS_SELECTOR, "td.title a")
                date = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                results.append({
                    "title": a.text.strip(),
                    "href":  a.get_attribute("href"),
                    "date":  date.text.strip(),
                })
            except (NoSuchElementException, StaleElementReferenceException):
                continue  # 헤더 행이나 빈 행은 무시

        return results

    def next_page(self, current_page):
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, str(current_page + 1)))
            )
            self.driver.execute_script("arguments[0].scrollIntoView()", btn)
            btn.click()

            # URL 변화로 페이지 이동 완료 확인
            self.wait.until(EC.url_contains(f"page={current_page + 1}"))
            return True
        except TimeoutException:
            return False  # 마지막 페이지

    def scrape(self, stock_code, pages=5):
        self.go_to_board(stock_code)
        all_data = []

        for page in range(1, pages + 1):
            print(f"[{page}/{pages}] 수집 중...")
            all_data.extend(self.collect_page())

            if page < pages:
                if not self.next_page(page):
                    print("마지막 페이지 도달")
                    break
                time.sleep(0.5)   # 서버 부하 방지 (유일하게 허용되는 sleep)

        return all_data

# 실행
scraper = StockBoardScraper(driver)
data = scraper.scrape("005930", pages=5)
print(f"총 {len(data)}건 수집")
```

다음 단계인 데이터 수집과 저장(CSV/JSON 저장, 페이지네이션 완전 자동화)으로 넘어가면 이 코드를 완성할 수 있습니다. 원하시면 이어서 설명드리겠습니다.