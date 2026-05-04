데이터 수집과 저장은 지금까지 배운 모든 기술의 종착점입니다. 전체 파이프라인을 직접 조작해볼 수 있는 인터랙티브 도구를 먼저 보여드리겠습니다."필드 선택" 탭에서 원하는 필드를 켜고 끄면 생성될 코드가 실시간으로 바뀝니다. "저장 형식" 탭에서 CSV / JSON / SQLite 출력을 미리보고, "파이프라인 시뮬레이션" 탭에서 실제 수집 흐름을 확인해보세요. 이제 각 단계를 코드와 함께 자세히 설명드립니다.

---

## 1. 텍스트와 속성 추출 — 기본기

```python
from selenium.webdriver.common.by import By

row = driver.find_element(By.CSS_SELECTOR, ".post-row")

# ── 텍스트 추출 ────────────────────────────────────────
row.text                          # 요소 전체 텍스트 (자식 포함)
row.find_element(By.CSS_SELECTOR, ".title a").text   # 특정 자식 텍스트

# ── 속성 추출 ─────────────────────────────────────────
element.get_attribute("href")     # 링크 URL
element.get_attribute("src")      # 이미지 경로
element.get_attribute("class")    # 클래스명
element.get_attribute("data-id")  # data-* 커스텀 속성
element.get_attribute("innerHTML")# 내부 HTML 전체
element.get_attribute("value")    # input 입력값

# ── 텍스트 정제 ───────────────────────────────────────
text = element.text.strip()                      # 앞뒤 공백 제거
num  = element.text.strip().replace(",", "")     # 숫자에서 콤마 제거
num  = int(num) if num.isdigit() else 0          # 정수 변환
```

---

## 2. 페이지네이션 완전 자동화

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def scrape_all_pages(driver, stock_code, max_pages=10):
    wait = WebDriverWait(driver, 10)
    driver.get(f"https://finance.naver.com/item/board.naver?code={stock_code}")
    all_results = []
    page = 1

    while page <= max_pages:
        # 현재 페이지 게시글 수집
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "table.type2 tr td.title")
            ))
        except TimeoutException:
            print(f"페이지 {page} 로드 실패 — 종료")
            break

        rows = driver.find_elements(By.CSS_SELECTOR, "table.type2 tr")
        for row in rows:
            try:
                a    = row.find_element(By.CSS_SELECTOR, "td.title a")
                date = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                all_results.append({
                    "page":   page,
                    "title":  a.text.strip(),
                    "link":   a.get_attribute("href"),
                    "date":   date.text.strip(),
                })
            except NoSuchElementException:
                continue

        print(f"페이지 {page} — {len(all_results)}건 누적")

        # 다음 페이지 버튼 탐색
        try:
            next_btn = wait.until(EC.element_to_be_clickable(
                (By.LINK_TEXT, str(page + 1))
            ))
            driver.execute_script("arguments[0].scrollIntoView()", next_btn)
            next_btn.click()
            page += 1
            time.sleep(0.5)   # 서버 부하 방지
        except TimeoutException:
            print("마지막 페이지 도달")
            break

    return all_results
```

---

## 3. CSV 저장

```python
import csv

def save_csv(data, filename="posts.csv"):
    if not data:
        print("저장할 데이터 없음")
        return

    fieldnames = list(data[0].keys())

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        # utf-8-sig: BOM 포함 — 엑셀에서 한글 깨짐 없음
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"CSV 저장 완료: {filename} ({len(data)}건)")

# 기존 파일에 이어쓰기 (누적 수집 시)
def append_csv(data, filename="posts.csv"):
    if not data:
        return
    import os
    file_exists = os.path.exists(filename)
    fieldnames = list(data[0].keys())

    with open(filename, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()   # 파일이 없을 때만 헤더 작성
        writer.writerows(data)
```

---

## 4. JSON 저장

```python
import json
from datetime import datetime

def save_json(data, filename="posts.json"):
    output = {
        "scraped_at": datetime.now().isoformat(),
        "count":      len(data),
        "data":       data,
    }
    with open(filename, "w", encoding="utf-8") as f:
        # ensure_ascii=False: 한글을 \uXXXX가 아닌 그대로 저장
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"JSON 저장 완료: {filename}")

# 기존 JSON에 항목 추가
def append_json(new_data, filename="posts.json"):
    import os
    existing = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f).get("data", [])

    all_data = existing + new_data
    save_json(all_data, filename)
```

---

## 5. SQLite 저장 — 중복 방지와 누적 수집에 강력

```python
import sqlite3
from datetime import datetime

def init_db(db_path="stock_posts.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            title      TEXT,
            link       TEXT UNIQUE,   -- UNIQUE: 동일 URL 중복 저장 방지
            author     TEXT,
            date       TEXT,
            views      TEXT,
            scraped_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    return conn

def save_to_db(conn, data, stock_code):
    inserted = 0
    for item in data:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO posts
                   (stock_code, title, link, author, date, views)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (stock_code,
                 item.get("title"),
                 item.get("link"),     # UNIQUE 제약으로 중복 자동 스킵
                 item.get("author"),
                 item.get("date"),
                 item.get("views"))
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                inserted += 1
        except sqlite3.Error as e:
            print(f"DB 오류: {e}")

    conn.commit()
    print(f"DB 저장: {inserted}건 신규 / {len(data)-inserted}건 중복 스킵")
    return inserted

# 사용 예
conn = init_db()
data = scrape_all_pages(driver, "005930")
save_to_db(conn, data, "005930")
conn.close()
```

---

## 6. 완성된 프로덕션급 수집기

지금까지 배운 내용을 모두 합친 최종 코드입니다.

```python
import csv, json, sqlite3, time, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager


class StockScraper:

    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.execute_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )

    # ── 단일 페이지 수집 ─────────────────────────────────
    def _scrape_page(self):
        results = []
        try:
            self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "table.type2 tr td.title")
            ))
        except TimeoutException:
            return results

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.type2 tr")
        for row in rows:
            try:
                a      = row.find_element(By.CSS_SELECTOR, "td.title a")
                date   = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                views  = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
                results.append({
                    "title":  a.text.strip(),
                    "link":   a.get_attribute("href"),
                    "date":   date.text.strip(),
                    "views":  views.text.strip().replace(",", ""),
                })
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return results

    # ── 전체 페이지 순회 ─────────────────────────────────
    def scrape(self, stock_code, max_pages=5):
        url = f"https://finance.naver.com/item/board.naver?code={stock_code}"
        self.driver.get(url)

        # 팝업 닫기
        try:
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_agree,.close"))
            )
            btn.click()
        except TimeoutException:
            pass

        all_data, page = [], 1
        while page <= max_pages:
            batch = self._scrape_page()
            all_data.extend(batch)
            print(f"[{page}/{max_pages}] {len(batch)}건 수집 → 누적 {len(all_data)}건")

            try:
                btn = self.wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, str(page + 1)))
                )
                self.driver.execute_script("arguments[0].scrollIntoView()", btn)
                btn.click()
                page += 1
                time.sleep(0.5)
            except TimeoutException:
                print("마지막 페이지")
                break

        return all_data

    # ── 저장 메서드 ───────────────────────────────────────
    def save_csv(self, data, path):
        if not data:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV 저장: {path} ({len(data)}건)")

    def save_json(self, data, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"scraped_at": datetime.now().isoformat(), "count": len(data), "data": data},
                f, ensure_ascii=False, indent=2
            )
        print(f"JSON 저장: {path}")

    def save_db(self, data, stock_code, db_path="posts.db"):
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT, title TEXT, link TEXT UNIQUE,
                date TEXT, views TEXT,
                scraped_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        inserted = sum(
            conn.execute(
                "INSERT OR IGNORE INTO posts (stock_code,title,link,date,views) VALUES(?,?,?,?,?)",
                (stock_code, r["title"], r["link"], r["date"], r["views"])
            ).rowcount
            for r in data
        )
        conn.commit(); conn.close()
        print(f"DB 저장: {inserted}건 신규 / {len(data)-inserted}건 중복 스킵")

    def quit(self):
        self.driver.quit()


# ── 실행 ──────────────────────────────────────────────────
if __name__ == "__main__":
    scraper = StockScraper(headless=False)   # 개발 중엔 False
    try:
        data = scraper.scrape("005930", max_pages=5)

        os.makedirs("data", exist_ok=True)
        today = datetime.now().strftime("%Y%m%d")
        scraper.save_csv(data,  f"data/samsung_{today}.csv")
        scraper.save_json(data, f"data/samsung_{today}.json")
        scraper.save_db(data, "005930")

        print(f"\n최종 수집: {len(data)}건")
    finally:
        scraper.quit()   # 오류 발생해도 드라이버 반드시 종료
```

---

## 7. 저장 형식 선택 기준

| 상황 | 권장 형식 | 이유 |
|------|-----------|------|
| 엑셀로 열어서 분석 | CSV (`utf-8-sig`) | 엑셀 호환, 한글 깨짐 없음 |
| 다른 Python 코드에서 가공 | JSON | 구조 보존, 로드 편의 |
| 반복 수집, 중복 방지 필요 | SQLite | `UNIQUE` 제약으로 자동 중복 스킵 |
| 대용량 분석 (pandas) | CSV + pandas | `pd.read_csv()`로 바로 분석 가능 |
| API 서버에 제공 | JSON | REST 응답 형식과 동일 |

---

이것으로 환경 설정 → 요소 선택 → 페이지 조작 → 대기 전략 → 데이터 수집·저장까지 Selenium의 전체 흐름을 완성했습니다. 다음 단계로 `pandas`를 이용한 수집 데이터 분석이나, 로그인이 필요한 사이트 처리, 또는 수집한 댓글의 감성 분석으로 이어가고 싶으시면 알려주세요.